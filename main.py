import random
import sys
import time

sys.path.append('lib')
from synth import *
from utils import *


def main():
    synth = Synth()

    pulse_rate = set_pulse_rate()

    print("\n### Starting performance ###")
    try:
        while True:
            scale_step = random.choice(synth.scale)
            synth.set_freq(scale_step)
            synth.play()
            time.sleep(pulse_rate)

    except KeyboardInterrupt:
        print("\n\n### STCV-Synth was stopped ###")

    finally:
        synth.stop()


if __name__ == "__main__":
    main()
