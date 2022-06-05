"""
Synthesizer abstraction containing the various elements to control it
as a tempered musical instrument.
"""

# Python Libraries
import os
from sys import platform
from typing import Union

# Third-Party Libraries
import numpy as np
import pyo

# Local Files
from constants import BASE_MULT_OPTIONS, BPM_SUBDIVISIONS, SCALES, \
    SUBDIVISION_OPTIONS, TONAL_CENTER_OPTIONS


class Synth():
    """
    List of all properties include:

        Synth properties:
            self.server
            self.amp_env
            self.osc

        Settings properties:
            self.base_hz
            self.base_key       # Key for easy matching against screen values
            self.base_mult_and_range    # As it relates to BASE_MULT_OPTIONS
            self.tonal_center
            self.oct_range
            self.scale          # tuple: (scale name, np.array structure)
            self.bpm
            self.subdivision
            self.pulse_rate
    """

    def __init__(self, config: dict) -> None:
        """
        Create a synthesizer object by instantiating an audio server using
        Pyo. Additionally, declare an oscillator and envelope generator,
        and run logic for setting the properties that will determine how
        frequencies and timings will be performed when executing the synth.
        """

        ###################
        ### INIT SERVER ###
        ###################

        # Create a server to handle all communications with
        # Portaudio and Portaudio MIDI.
        # The duplex parameter is used to initialize only the audio outputs.
        self.server = pyo.Server(config["sample_rate"], duplex=0)

        # Disable MIDI
        self.server.deactivateMidi()

        if platform == 'linux':
            # Set the default device of the computer (the one selected in the
            # system's audio preferences) as the output device for the server.
            self.server.setOutputDevice(pyo.pa_get_default_output())

        # the boot() function boots the server.
        # booting the server includes:
        #     - opening Audio and MIDI interfaces
        #     - setup of Sample Rate and Number of Channels
        self.server.boot()
        print("\tAudio server initialized")

        # Set the overall amplitude of the server.
        self.server.amp = 1.0

        # Start audio processing in the server.
        self.server.start()


        #######################
        ### INIT PROPERTIES ###
        #######################

        self.set_base(config["tonal_center"], config["base_multiplier"])
        self.set_oct_range(config["octave_range"])
        self.set_scale(config["scale_mode"] if config["scale_mode"] in SCALES else "dorian")
        self.set_bpm(config["bpm"])
        self.set_subdivision(config["subdivision"])
        self.set_pulse_rate()

        self._print_properties()

        # Maps inputs between 0 and 1 to a range of 20Hz to 20kHz using
        # a logarithmic scale.
        # REF: http://ajaxsoundstudio.com/pyodoc/api/classes/map.html
        self.filt_map = pyo.Map(200.0, 20000.0, 'log')

        # Create an envelope generator.
        self.amp_env = pyo.Adsr(attack=0.01,
                            decay=0.2,
                            sustain=0.5,
                            release=0.1,
                            dur=0.5,        # duration is expressed in seconds
                            mul=0.5)

        # Initialize oscillator.
        # Using a Sig object for defining the frequency is a faster
        # implementation. This is because simple arithmetic operations
        # involving audio objects will create a 'Dummy' object to hold the
        # modified signal, which will allocate memory for the audio stream
        # and add a processing task onto the CPU.
        self.freq_root = pyo.Sig(value=1000)
        self.osc_root = pyo.SuperSaw(freq=self.freq_root, mul=self.amp_env)

        # The filter will take in the oscillator at the input, and its
        # frequency will depend upon movement in the ST tilt.
        # MoogLP filter is a 4th orden Low-Pass Filter i.e., 24dB per octave.
        self.filt = pyo.MoogLP(self.osc_root, freq=1000)

        self.delay = pyo.Delay(self.filt, self.bpm / 16, 0.8)

        # Initialize mixer and add channels to the mixer.
        self.mixer = pyo.Mixer(outs=1, chnls=2)
        self.mixer.addInput(voice=0, input=self.filt)
        self.mixer.addInput(voice=1, input=self.delay)
        self.mixer.setAmp(vin=0, vout=0, amp=0.707)
        self.mixer.setAmp(vin=1, vout=0, amp=0.707)

        # Initialize reverb to enhance the audio signal. The balance will be
        # controlled by the Azimuth angle from the ST.
        # The 'out()' method routes the given module to the DAC.
        self.reverb = pyo.Freeverb(
            self.mixer[0], size=0.8, damp=0.8, bal=0.5
        ).out()

    def play(self) -> None:
        """
        Trigger the envelope generator.
        """
        self.amp_env.play()


    #######################
    ### SCALE FUNCTIONS ###
    #######################

    def set_base(self, tonal_center: str, mult_key: int) -> None:
        """
        The base is the lowest possible frequency of the synth. It is set by
        multiplying a tonal center (frequency) with a base multiplier, which
        sets the lowest accessible frequency.
        """
        # BASE_MULT_OPTIONS values are tuples containing the base multiplier,
        # as well as the maximum octave range available for that base.
        self.base_mult_and_range = BASE_MULT_OPTIONS[mult_key]
        self.base_key = mult_key
        self.tonal_center = tonal_center
        self.base_hz = TONAL_CENTER_OPTIONS[tonal_center] * \
            self.base_mult_and_range[0]

    def set_osc_freq(self, scale_step: int) -> None:
        """
        Set oscillator frequency by converting a given scale step to
        frenquency.
        """
        self.freq_root.value = float(self.base_hz * 2 ** (scale_step / 12))

    def set_oct_range(self, oct_range: int) -> None:
        """
        Verify that the set octave range is lesser than or equal to the
        maximum octave range for the selected frequency base multiplier.
        If the set octave range exceeds this maximum octave range, the
        octave range will be truncated to match the maximum multiplier for
        the given frequency base.
        """
        # The minimum octave range available is 1.
        if oct_range < 1:
            self.oct_range = 1
            return

        # Truncate value to maximum availble octave range for the selected
        # frequency base if it exeeds it. The second value of the tuple
        # contained in base_mult_and_range contains the maximum octave value
        # available for the selected base.
        if oct_range > self.base_mult_and_range[1]:
            self.oct_range = self.base_mult_and_range[1]
            return

        self.oct_range = oct_range

    def set_scale(self, scale: str) -> None:
        """
        Sets the scale that will be used for mapping the input data.
        Setting the scale implies storing the name of the currently selected
        scale, as well as the twelve-tone system structure of the scale. This
        representation takes into account the octave range of the scale.
        """
        # Tuple with the name of the currently selected scale, and the
        # structure of the scale as a np.array matching the scale structure,
        # with extended number of steps to match the number of octaves.
        self.scale = (scale, np.hstack(
            [np.hstack(SCALES[scale]) + i * 12 for i in range(self.oct_range)]
        ))

    def set_bpm(self, bpm: Union[int, float]) -> None:
        """
        Method sets the global BPM of the synthesizer, which is used
        in combination with the pulse rate for pulsing mode, as well
        as future implementation of time-domain audio effects.
        """
        self.bpm = 60 / bpm

    def set_subdivision(self, subdivision: int) -> None:
        """
        Method sets the sub-division that will be applied to the BPM when
        setting the pulse rate of the synthesizer.
        """
        self.subdivision = subdivision

    def set_pulse_rate(self) -> None:
        """
        The pulse rate is effectively the implemented subdivision of
        the synthesizer's BPM.
        """
        self.pulse_rate = self.bpm / BPM_SUBDIVISIONS[self.subdivision]

    def _print_properties(self) -> None:
        """
        Print all of the Synth's set properties.
        """
        print(f"\n\tTonal Center: {self.tonal_center}")
        print(f"\tBase Fequency: {self.base_hz}Hz")
        print(f"\n\tCurrent Scale: {self.scale[0].capitalize()}")
        print(f"\tOctave Range: {self.oct_range}")
        print(f"\tScale Structure: {self.scale[1]}")
        print(f"\n\tBPM = Quarter Note {round(60 / self.bpm)}")
        print(f"\tSub-Division = {SUBDIVISION_OPTIONS[self.subdivision]}")
        print(f"\tPulse rate = {self.pulse_rate:.2f} seconds")


    ########################
    ### SERVER FUNCTIONS ###
    ########################

    def stop_server(self) -> None:
        """
        Stops the audio server.
        """
        print("\n\tShutting down the audio server.\n")
        # Stop the server
        self.server.stop()


    ##############
    ### RENDER ###
    ##############
    def get_render_path(self) -> str:
        """
        Create a render path that prevents previous files from being
        overwritten.
        Implemented in the synth abstraction for easy access of the
        synth properties.
        """
        out_folder = "renders"

        # Determine if output folder exists and create it if it does not
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        # Determine if output file has been created
        i = 0
        while True:
            # ':02d' is used to express ints with two digits.
            out_file = \
                f"{self.tonal_center}_{self.scale[0]}_bpm{int(60/self.bpm)}_{i:02d}"
            if not os.path.exists(os.path.join(out_folder, out_file + ".wav")):
                break
            i += 1

        return os.path.join(out_folder, out_file)
