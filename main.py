import random
import sys
import time

sys.path.append('lib')
from synth import *


def main():
    synth = Synth()

    pulse_rate = set_pulse_rate()

    try:
        while True:
            scale_step = random.choice(synth.scale)
            synth.set_freq(scale_step)
            synth.play()
            time.sleep(pulse_rate)

    except KeyboardInterrupt:
        synth.stop()


if __name__ == "__main__":
    main()
