# Python Libraries
import os
from sys import platform
from typing import Union

# Third-Party Libraries
import numpy as np
from pyo import *

# Local Files
from constants import *


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

    def __init__(self, audio_sample_rate: int) -> None:
        """
        Create a synthesizer object by instantiating an audio server using
        Pyo. Additionally, declare an oscillator and envelope generator,
        and run logic for setting the properties that will determine how
        frequencies and timings will be performed when executing the synth.
        """
        # Create a server to handle all communications with
        # Portaudio and Portaudio MIDI.
        self.server = Server(audio_sample_rate)

        # Disable MIDI
        self.server.deactivateMidi()

        if platform == 'linux':
            # Set the default device of the computer (the one selected in the
            # system's audio preferences) as the output device for the server.
            self.server.setOutputDevice(pa_get_default_output())

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

        self.set_properties()

        # Maps inputs between 0 and 1 to a range of 20Hz to 20kHz using
        # a logarithmic scale.
        # REF: http://ajaxsoundstudio.com/pyodoc/api/classes/map.html
        self.filt_map = Map(200.0, 20000.0, 'log')

        # Create an envelope generator.
        self.amp_env = Adsr(attack=0.01,
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
        self.freq_root = Sig(value=1000)
        self.osc_root = SuperSaw(freq=self.freq_root, mul=self.amp_env)

        # The filter will take in the oscillator at the input, and its
        # frequency will depend upon movement in the ST tilt.
        # MoogLP filter is a 4th orden Low-Pass Filter i.e., 24dB per octave.
        self.filt = MoogLP(self.osc_root, freq=1000)

        self.delay = Delay(self.filt, self.bpm / 16, 0.8)

        # Initialize mixer and add channels to the mixer.
        self.mixer = Mixer(outs=1, chnls=2)
        self.mixer.addInput(voice=0, input=self.filt)
        self.mixer.addInput(voice=1, input=self.delay)
        self.mixer.setAmp(vin=0, vout=0, amp=0.707)
        self.mixer.setAmp(vin=1, vout=0, amp=0.707)

        # Initialize reverb to enhance the audio signal. The balance will be
        # controlled by the Azimuth angle from the ST.
        # The 'out()' method routes the given module to the DAC.
        self.reverb = Freeverb(
            self.mixer[0], size=0.8, damp=0.8, bal=0.5
        ).out()

    def play(self) -> None:
        """
        Trigger the envelope generator.
        """
        self.amp_env.play()

    """
    SCALE FUNCTIONS
    """

    def set_base(self, tonal_center: str = DEF_TONAL_CENTER,
                 mult_key: int = DEF_BASE_MULTIPLIER) -> None:
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

    def set_oct_range(self, oct_range: int = DEF_NUM_OCTAVES) -> None:
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

    def set_scale(self, scale: str = DEF_SCALE) -> None:
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

    def set_bpm(self, bpm: Union[int, float] = DEF_BPM) -> None:
        """
        Method sets the global BPM of the synthesizer, which is used
        in combination with the pulse rate for pulsing mode, as well
        as future implementation of time-domain audio effects.
        """
        self.bpm = 60 / bpm

    def set_subdivision(self, subdivision: int = DEF_SUBDIVISION) -> None:
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

    """
    SELECT SETTINGS
    """

    def set_properties(self) -> None:
        """
        Sets the synthesizer settings upon launching the program.
        It can either follow a default init routine, or a custom one
        that allows the user to specify their settings of choice.
        """
        # Check if the user would like to use default settings.
        x = input("""
        Would you like to use the synthesizer's defaults?
        (Any other input will implement defaults).
        y/n: """)

        # Set default settings
        if x.lower() != "n":
            self.set_base()
            self.set_oct_range()
            self.set_scale()
            self.set_bpm()
            self.set_subdivision()
            self.set_pulse_rate()
            self.print_properties()

        # Prompt for custom settings
        else:
            # Set the synthesizer frequency base (i.e., tonal center)
            print("\n\tSelect tonal center (use letters)")
            [print(f"\t\t{k}:\t{v}") for k, v in TONAL_CENTER_OPTIONS.items()]
            print(f"\tUnavailable inputs default to {DEF_TONAL_CENTER}.")
            tonal_center = input("\n\tTonal Center: ").capitalize()
            if tonal_center not in TONAL_CENTER_OPTIONS:
                tonal_center = DEF_TONAL_CENTER

            # Set the base multiplier
            print("\n\tSelect base multiplier (select numeric option):")
            [
                print(f"\t\t{k}:\tMultiplier:\t{v[0]}\tMax 8ve range:\t{v[1]}")
                for k, v in BASE_MULT_OPTIONS.items()
            ]
            print(f"\tUnavailable inputs default to option \
                {DEF_BASE_MULTIPLIER}")
            base_mult = input("\n\tBase Multiplier: ")
            if base_mult not in BASE_MULT_OPTIONS:
                base_mult = DEF_BASE_MULTIPLIER

            self.set_base(tonal_center, base_mult)

            # Set octave range and scale
            self.sel_oct_range_and_scale()

            # Set clock
            bpm = int(input("\n\tChoose quarter note BPM: "))
            if isinstance(bpm, (int, float)) and bpm != 0:
                self.set_bpm(abs(bpm))
            else:
                self.set_bpm()

            # Set subdivision for pulse rate
            print("\tAvailable sub-division options:")
            [print(f"\t\t{k}: {v}") for k, v in SUBDIVISION_OPTIONS.items()]
            print(f"\tUnavailable inputs default to \
                {SUBDIVISION_OPTIONS[DEF_SUBDIVISION]}.")

            subdivision = input("\n\tSelect subdivision option (use index): ")
            if subdivision in BPM_SUBDIVISIONS.keys():
                self.set_subdivision(subdivision)
            else:
                self.set_subdivision()

            self.set_pulse_rate()

            # Display all synth properties to the user.
            self.print_properties()

    def sel_oct_range_and_scale(self) -> None:
        """
        Display and prompt user to choose a scale and an octave range.
        Available scales and ranges are declared in 'constants.py'.
        This function is only run when initializing the synth, and
        choosing custom settings.
        """
        # Display available scales to the user.
        print("\n\tIndex of scales")
        [print(f"\t\t{k}") for k in SCALES.keys()]

        # Prompt user to choose a scale.
        while True:
            scale = input("\n\tSelect your scale (type the name): ").lower()
            # Verify that their selected scale is an available scale.
            if scale in SCALES.keys():
                break
            else:
                print("Please input the name of an available scale.")

        # Prompt user to choose an octave range.
        while True:
            try:
                oct_range = int(input(
                    f"\tSelect number of octaves (max value for selected scale is {self.base_mult_and_range[1]}): "
                ))
                break
            # Verify that input is a number.
            except ValueError:
                print(f"Please choose a number between 1 and \
                    {self.base_mult_and_range[1]} inclusive. If selection is \
                    lesser than 1, the octave range will be set to one. If \
                    the number exceeds the maximum octave range for the \
                    selected base ({self.base_mult_and_range[1]}), it will \
                    be truncated to that maximum value.")

        # Set chosen values.
        self.set_oct_range(oct_range)
        self.set_scale(scale)

    def print_properties(self) -> None:
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

    """
    SERVER FUNCTIONS
    """
    def stop_server(self) -> None:
        """
        Stops the audio server.
        """
        print("\n\tShutting down the audio server.\n")
        # Stop the server
        self.server.stop()

    """
    RENDER
    """
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
