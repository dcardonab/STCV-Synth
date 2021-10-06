from pyo import *

BASE_NOTE = 110

class Synth():

    def __init__(self):
        # the boot() function boots the server
        # booting the server includes:
        #     - opening Audio and MIDI interfaces
        #     - setup of Sample Rate and Number of Channels
        self.server = Server().boot()
        print("\tPyo server initialized")

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


    def pitch(self, freq):
        self.osc.freq = freq

    def play(self):
        # Play the envelope generator
        self.amp_env.play()

    def stop(self):
        # Stop the server
        self.server.stop()