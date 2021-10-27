import numpy as np
from pyo import *
from sys import platform

# Local files
from constants import *
from utils import print_scales


class Synth():

    def __init__(self):
        # Create a server to handle all communications with
        # Portaudio and Portaudio MIDI
        self.server = Server()

        # Select the device with the 'default' name
        if platform == "linux":
            pa_list_devices()
            print("Select device with 'default' name")
            device = int(input("Select audio device: "))
            self.server.setOutputDevice(device)

        # the boot() function boots the server
        # booting the server includes:
        #     - opening Audio and MIDI interfaces
        #     - setup of Sample Rate and Number of Channels
        self.server.boot()
        print("\n\tPyo server initialized")

        # Start audio processing in the server
        self.server.start()
        print("\tAudio running")

        # Create an envelope generator
        self.amp_env = Adsr(attack=0.01,
                            decay=0.2,
                            sustain=0.5,
                            release=0.1,
                            dur=0.5,        # duration is expressed in seconds
                            mul=0.5)

        # Initialize oscillator
        self.osc = Sine(mul=self.amp_env).out()

        self.set_base()

        self.select_scale()

    def set_freq(self, scale_step):
        f = float(self.base * 2 ** (scale_step / 12))
        print(f"Oscillator Frequency: {f:.2f}")
        self.osc.freq = f

    def play(self):
        # Play the envelope generator
        self.amp_env.play()

    def stop(self):
        print("Shutting down the audio server.\n")
        # Stop the server
        self.server.stop()

    def set_base(self):
        # The base is the lowest possible note of the synth
        option = input("""
        Select lowest frequency option:
            1 = 110Hz
            2 = 220Hz
            3 = 440Hz
        (Note: Any other input will default to 220Hz)
        """)

        if option in bases.keys():
            freq = bases[option]
        else:
            freq = bases['2']

        self.base = freq

    def select_scale(self):
        print_scales()

        while True:
            scale = input("Select your scale (type the name): ")
            if scale in scales.keys():
                break
            else:
                print("Please input an available scale.")

        while True:
            n_octaves = int(input("Select number of octaves: "))
            if n_octaves >= 1 or n_octaves <= 8:
                break
            else:
                print("Please choose a number between 1 and 8 inclusive.")

        # Extend number of steps in the scale to match the number of octaves
        self.scale = np.hstack(
            [np.hstack(scales[scale]) + i * 12 for i in range(n_octaves)]
        )

        print(self.scale)
