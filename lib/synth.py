import numpy as np
import os
from pyo import *
from sys import platform

# Local files
from constants import *


DEF_BASE_MULTIPLIER = '4'
DEF_BPM = 100
DEF_SUBDIVISION = '16'
DEF_NUM_OCTAVES = 2
DEF_SCALE = 'dorian'
DEF_TONAL_CENTER = 'A'


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

    def __init__(self):
        print("\n\n\t##### Initializing Synthesizer #####\n")
        # Create a server to handle all communications with
        # Portaudio and Portaudio MIDI
        self.server = Server(sr=48000)

        # Select the device with the 'default' name
        if platform == "linux":
            pa_list_devices()
            print("\tSelect device with 'default' name")
            device = int(input("\n\tSelect audio device: "))
            self.server.setOutputDevice(device)

        # the boot() function boots the server
        # booting the server includes:
        #     - opening Audio and MIDI interfaces
        #     - setup of Sample Rate and Number of Channels
        self.server.boot()
        print("\tAudio server initialized")

        # Start audio processing in the server
        self.server.start()

        # Create an envelope generator
        self.amp_env = Adsr(attack=0.01,
                            decay=0.2,
                            sustain=0.5,
                            release=0.1,
                            dur=0.5,        # duration is expressed in seconds
                            mul=0.5)

        # Initialize oscillator
        self.osc = Sine(mul=self.amp_env).out()

        self.settings()

    def play(self):
        # Play the envelope generator
        self.amp_env.play()

    #######################
    ### SCALE FUNCTIONS ###
    #######################

    def select_scale(self):
        # Display available scales to the user
        print("\n\tIndex of scales")
        [print(f"\t\t{k}") for k in scales.keys()]

        while True:
            scale = input("\n\tSelect your scale (type the name): ").lower()
            if scale in scales.keys():
                break
            else:
                print("Please input the name of an available scale.")

        while True:
            n_octaves = int(input("\tSelect number of octaves: "))
            # The second value of the tuple contained in current_base contains
            # the maximum octave value available for the selected base.
            if n_octaves >= 1 or n_octaves <= self.cur_base[1]:
                break
            else:
                print(f"""
                Please choose a number between 1 and {self.cur_base[1]} inclusive.
                If selection exceeds maximum 8ve range for the selected base,
                it will be truncated to that maximum value.
                """)

        self.set_scale(scale, n_octaves)

    # The base is the lowest possible frequency of the synth
    def set_base(self, tonal_cntr=DEF_TONAL_CENTER, mult=DEF_BASE_MULTIPLIER):
        # Mult value is stored in current_base for
        # accessing it when defining scale
        self.cur_base = base_mult_options[mult]
        self.cur_tonal_center = tonal_cntr
        self.base_hz = tonal_center_options[tonal_cntr] * self.cur_base[0]
        print(f"\n\tBase frequency: {self.base_hz}Hz")

    def set_freq(self, scale_step):
        f = float(self.base_hz * 2 ** (scale_step / 12))
        print(f"\tOscillator Frequency: {f:.2f}")
        self.osc.freq = f

    def set_scale(self, scale=DEF_SCALE, n_octaves=DEF_NUM_OCTAVES):
        # Make sure the octave length does not exceed the 8ve range for the
        # selected base. This is done when the octave base changes.
        if n_octaves <= self.cur_base[1]:
            self.oct_range = n_octaves
        else:
            self.oct_range = self.cur_base[1]

        # Tuple with the name of the currently selected scale, and the
        # structure of the scale as a np.array matching the scale structure,
        # with extended number of steps to match the number of octaves.
        self.scale = (scale, np.hstack(
            [np.hstack(scales[scale]) + i * 12 for i in range(self.oct_range)]
        ))
        print(f"\n\tCurrent Scale: {self.scale[0].capitalize()}")
        print(f"\tScale structure: {self.scale[1]}")

    ################
    ### SETTINGS ###
    ################

    def set_bpm(self, bpm=DEF_BPM):
        self.bpm = 60 / bpm
        print(f"\n\tBPM: Quarter Note {bpm}")

    def set_pulse_rate(self, sub_division=DEF_SUBDIVISION):
        self.pulse_rate = self.bpm / bpm_sub_divisions[sub_division]
        print(f"\n\tSub-Division = {sub_division_options[sub_division]}")
        print(f"\tPulse rate = {self.pulse_rate:.2f} seconds")

    def settings(self):
        # Check if the user would like to use default settings.
        x = input("""
        Would you like to use the synthesizer's defaults?
        (Any other input will implement defaults).
        y/n: """)

        # Set default settings
        if x.lower() != "n":
            self.set_base()
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

            # Set scale
            self.select_scale()

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

    ########################
    ### SERVER FUNCTIONS ###
    ########################

    def stop_server(self):
        print("\tShutting down the audio server.\n")
        # Stop the server
        self.server.stop()

    ##############
    ### RENDER ###
    ##############

    def get_render_path(self):
        """
        Ensure that previous files are not overwritten by using the
        'exists()' method with an iterator.
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
