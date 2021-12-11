"""
SensorTile Constants
"""
ST_FIRMWARE_NAME = 'AM1V310'

# Accelerometer magnitude range
# Since the accelerometer of the ST is calibrated to a maximum
# value of 2G per axis, the approximate maximum magnitude will
# be 3464 G. The minimum magnitude value will approximately be
# 1030 G, according to tests that kept the ST stationary.
MIN_ACC_MAGNITUDE = 1030
MAX_ACC_MAGNITUDE = 3464
MIN_TILT = 0
MAX_TILT = 180
MIN_AZIMUTH = -180
MAX_AZIUMTH = 180

# SensorTile GATT Handles
ST_HANDLES = {
    "environment": 13,
    "motion": 16,
    "quaternions": 28
}

# Hand wearing the ST
ST_WEARING_HAND = {
    "Left": 0,
    "Right": 1
}

"""
Synthesizer Constants
"""
DEF_BASE_MULTIPLIER = '1'
DEF_BPM = 100
DEF_SUBDIVISION = '16'
DEF_NUM_OCTAVES = 2
DEF_SCALE = 'dorian'
DEF_TONAL_CENTER = 'A'

# Performance Mode
SYNTH_MODE = {
    "Pulse": 0,
    "Sustain": 1
}

# Tempered Scales
SCALES = {
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
BPM_SUBDIVISIONS = {
    "1": 0.25,
    "2": 0.5,
    "3": 0.75,
    "4": 1,
    "6": 1.5,
    "8": 2,
    "12": 3,
    "16": 4,
}

SUBDIVISION_OPTIONS = {
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
TONAL_CENTER_OPTIONS = {
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
BASE_MULT_OPTIONS = {
    "-2": (0.25, 7),
    "-1": (0.5, 6),
    "0": (1, 5),
    "1": (2, 4),
    "2": (4, 3),
    "3": (8, 2),
    "4": (16, 1),
}
