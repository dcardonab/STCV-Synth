import random
import sys
import time

sys.path.append('lib')
from scales import *
from synth import *


def main():
    synth = Synth()

    print_scales()

    try:
        while True:
            f = random.randrange(220, 880)
            print(f"Oscillator Frequency: {f}")
            synth.pitch(f)
            synth.play()
            time.sleep(0.5)

    except KeyboardInterrupt:
        synth.stop()


if __name__ == "__main__":
    main()