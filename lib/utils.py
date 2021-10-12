""" Helper functions """

from constants import *


def set_bpm():
    bpm = 60 / int(input("Choose BPM (in quarter notes): "))
    print(bpm)
    return bpm


def set_pulse_rate():
    bpm = set_bpm()
    option = input("""
    Select sub-division option:
        1 = Whole Notes
        2 = Half Notes
        3 = Half Note Triplet
        4 = Quarter Notes
        6 = Quarter Note Triplet
        8 = Eigth Notes
        12 = Eigth Note Triplet
        16 = Sixteenth Notes
    (Note: Any other input will default to Sixteenth Notes)
    """)

    if option in sub_divisions.keys():
        pulse_rate = bpm / sub_divisions[option]
    else:
        pulse_rate = bpm / sub_divisions['16']

    print(f"Pulse rate = {pulse_rate}")

    return pulse_rate


def print_scales():
    # List available scales
    print("\nIndex of scales")
    [print(f"\t{k}") for k in scales.keys()]
    print()
