import numpy as np
import os
from pyo import *
from sys import platform
from typing import Union

# Local files
from constants import *


class Synth():
    """
    List of all properties include:

        Synth properties:
            self.server
            self.amp_env
            self.osc

        Settings properties:
            self.cur_base       # As it relates to base_mult_options
            self.cur_tonal_center
            self.base_hz
            self.oct_range
            self.scale          # tuple: (scale name, np.array structure)
            self.bpm
            self.pulse_range
    """

    def __init__(self, audio_sample_rate: int) -> None:
        """
        Create a synthesizer object by instantiating an audio server using
        Pyo. Additionally, declare an oscillator and envelope generator,
        and run logic for setting the properties that will determine how
        frequencies and timings will be performed when executing the synth.
        """
        print("\n\n\t##### Initializing Synthesizer #####\n")
        # Create a server to handle all communications with
        # Portaudio and Portaudio MIDI.
        self.server = Server(audio_sample_rate)

        # Linux requires selecting the device with 'default' name.
        if platform == "linux":
            self.set_output_device()

        # the boot() function boots the server.
        # booting the server includes:
        #     - opening Audio and MIDI interfaces
        #     - setup of Sample Rate and Number of Channels
        self.server.boot()
        print("\tAudio server initialized")

        # Start audio processing in the server.
        self.server.start()

        # Create an envelope generator.
        self.amp_env = Adsr(attack=0.01,
                            decay=0.2,
                            sustain=0.5,
                            release=0.1,
                            dur=0.5,        # duration is expressed in seconds
                            mul=0.5)

        # Initialize oscillator.
        self.osc = Sine(mul=self.amp_env).out()

        self.settings()

    def play(self) -> None:
        """
        Trigger the envelope generator.
        """
        self.amp_env.play()

    """
    SCALE FUNCTIONS
    """

    def set_base(self, tonal_cntr: str = DEF_TONAL_CENTER,
                 mult: str = DEF_BASE_MULTIPLIER) -> None:
        """
        The base is the lowest possible frequency of the synth. It is set by
        multiplying a tonal center (frequency) with a base multiplier, which
        sets the lowest accessible frequency.
        """
        # base_mult_options values are tuples containing the base multiplier,
        # as well as the maximum octave range available for that base.
        self.cur_base = base_mult_options[mult]
        self.cur_tonal_center = tonal_cntr
        self.base_hz = tonal_center_options[tonal_cntr] * self.cur_base[0]
        print(f"\n\tBase frequency: {self.base_hz}Hz")

    def set_freq(self, scale_step: int) -> None:
        """
        Set frequency by converting a given scale step to frenquency.
        """
        f = float(self.base_hz * 2 ** (scale_step / 12))
        print(f"\tOscillator Frequency: {f:.2f}")
        self.osc.freq = f

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
        # contained in cur_base contains the maximum octave value
        # available for the selected base.
        if oct_range > self.cur_base[1]:
            self.oct_range = self.cur_base[1]
            return

        self.oct_range = oct_range

    def sel_oct_range_and_scale(self) -> None:
        """
        Display and prompt user to choose a scale and an octave range.
        Available scales and ranges are declared in 'constants.py'.
        This function is only run when initializing the synth, and 
        choosing custom settings.
        """
        # Display available scales to the user.
        print("\n\tIndex of scales")
        [print(f"\t\t{k}") for k in scales.keys()]

        # Prompt user to choose a scale.
        while True:
            scale = input("\n\tSelect your scale (type the name): ").lower()
            # Verify that their selected scale is an available scale.
            if scale in scales.keys():
                break
            else:
                print("Please input the name of an available scale.")

        # Prompt user to choose an octave range.
        while True:
            try:
                oct_range = int(input("\tSelect number of octaves: "))
                break
            # Verify that input is a number.
            except ValueError:
                print(f"Please choose a number between 1 and \
                    {self.cur_base[1]} inclusive. If selection is lesser \
                    than 1, the octave range will be set to one. If the \
                    number exceeds the maximum octave range for the selected \
                    base ({self.cur_base[1]}), it will be truncated to that \
                    maximum value.")

        # Set chosen values.
        self.set_oct_range(oct_range)
        self.set_scale(scale)

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
            [np.hstack(scales[scale]) + i * 12 for i in range(self.oct_range)]
        ))
        print(f"\n\tCurrent Scale: {self.scale[0].capitalize()}")
        print(f"\tScale structure: {self.scale[1]}")

    """
    SETTINGS
    """

    def set_bpm(self, bpm: float = DEF_BPM) -> None:
        """
        Method sets the global BPM of the synthesizer, which is used
        in combination with the pulse rate for pulsing mode, as well
        as future implementation of time-domain audio effects.
        """
        self.bpm = 60 / bpm
        print(f"\n\tBPM: Quarter Note {bpm}")

    def set_pulse_rate(self, sub_division: str = DEF_SUBDIVISION) -> None:
        """
        The pulse rate is effectively the implemented subdivision of
        the synthesizer's BPM.
        """
        self.pulse_rate = self.bpm / bpm_sub_divisions[sub_division]
        print(f"\n\tSub-Division = {sub_division_options[sub_division]}")
        print(f"\tPulse rate = {self.pulse_rate:.2f} seconds")

    def settings(self) -> None:
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
            self.set_pulse_rate()

        # Prompt for custom settings
        else:
            # Set the synthesizer frequency base (i.e., tonal center)
            print("\n\tSelect tonal center (use letters)")
            [print(f"\t\t{k}:\t{v}") for k, v in tonal_center_options.items()]
            print(f"\tUnavailable inputs default to {DEF_TONAL_CENTER}.")
            tonal_center = input("\n\tTonal Center: ").capitalize()
            if tonal_center not in tonal_center_options:
                tonal_center = DEF_TONAL_CENTER

            # Set the base multiplier
            print("\n\tSelect base multiplier (select numeric option):")
            [
                print(f"\t\t{k}: Multiplier:\t{v[0]}\tMax 8ve range:\t{v[1]}") 
                for k, v in base_mult_options.items()
            ]
            print(f"\tUnavailable inputs default to option {DEF_BASE_MULTIPLIER}")
            base_mult = input("\n\tBase Multiplier: ")
            if base_mult not in base_mult_options:
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
            [print(f"\t\t{k}: {v}") for k, v in sub_division_options.items()]
            print(f"\tUnavailable inputs default to {sub_division_options[DEF_SUBDIVISION]}.")
            sub_div = input("\n\tSelect sub-division option (use index): ")

            if sub_div in bpm_sub_divisions.keys():
                self.set_pulse_rate(sub_div)
            else:
                self.set_pulse_rate()

    """
    SERVER FUNCTIONS
    """

    def stop_server(self) -> None:
        """
        Stops the audio server.
        """
        print("\tShutting down the audio server.\n")
        # Stop the server
        self.server.stop()

    def set_output_device(self) -> None:
        """
        Used in Linux to select the correct audio device. Make sure to select
        the 'default' named device for proper operation of the Pyo server.
        """
        available_devices = pa_list_devices()

        # Automatic selection of corresponding device.
        for device in available_devices:
            if "name: default" in device:
                if device[1] == ':':
                    device_number = int(device[0])
                elif device[2] == ':':
                    device_number = int(device[0:2])
        
        # Manual selection if automatic selection fails.
        if not device_number:
            print("\tSelect device with 'default' name")
            device_number = int(input("\n\tSelect audio device: "))
            
        self.server.setOutputDevice(device)

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
            out_file = f"{self.cur_tonal_center}_{self.scale[0]}_bpm{int(60/self.bpm)}_{i:02d}"
            if not os.path.exists(os.path.join(out_folder, out_file + ".wav")):
                break
            i += 1

        return os.path.join(out_folder, out_file)
