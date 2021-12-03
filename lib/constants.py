# Tempered Scales
scales = {
    # Diatonic Modes
    "ionian": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "har_minor": [0, 2, 3, 5, 7, 8, 11],
    "mel_minor": [0, 2, 3, 5, 7, 9, 11],
    # Symmetrical Scales
    "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    # Pentatonic Modes
    "1st_pentatonic": [0, 3, 5, 7, 10],
    "2nd_pentatonic": [0, 2, 4, 7, 9],
    "3rd_pentatonic": [0, 2, 5, 7, 10],
    "4th_pentatonic": [0, 3, 5, 8, 10],
    "5th_pentatonic": [0, 2, 5, 7, 9],
    "whole_tone": [0, 2, 4, 6, 8, 10],
}

# BPM sub-divisions
bpm_sub_divisions = {
    "1": 0.25,
    "2": 0.5,
    "3": 0.75,
    "4": 1,
    "6": 1.5,
    "8": 2,
    "12": 3,
    "16": 4,
}

sub_division_options = {
    "1": "Whole Notes",
    "2": "Half Notes",
    "3": "Half Note Triplet",
    "4": "Quarter Notes",
    "6": "Quarter Note Triplet",
    "8": "Eigth Notes",
    "12": "Eigth Note Triplet",
    "16": "Sixteenth Notes",
}

# Music Key and Multiplier Options
tonal_center_options = {
    "A": 110,
    "A#": 116.54,
    "Bb": 116.54,
    "B": 123.47,
    "C": 130.81,
    "C#": 138.59,
    "Db": 138.59,
    "D": 146.83,
    "D#": 155.56,
    "Eb": 155.56,
    "E": 164.81,
    "F": 174.61,
    "F#": 185,
    "Gb": 185,
    "G": 196,
    "G#": 207.65,
    "Ab": 207.65,
}

# Each key holds a tuple containing the base multiplier
# and the maximum octave range for that multiplier.
base_mult_options = {
    "1": (0.25, 7),
    "2": (0.5, 6),
    "3": (1, 5),
    "4": (2, 4),
    "5": (4, 3),
    "6": (8, 2),
    "7": (16, 1),
}

# SensorTile GATT Handles
ST_handles = {"environment": 13, "motion": 16, "quaternions": 28}
