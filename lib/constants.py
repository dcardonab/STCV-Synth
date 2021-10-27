# Tempered Scales
scales = {
    # Diatonic Modes
    'ionian':       [0, 2, 4, 5, 7, 9, 11],
    'dorian':       [0, 2, 3, 5, 7, 9, 10],
    'phrygian':     [0, 1, 3, 5, 7, 8, 10],
    'lydian':       [0, 2, 4, 6, 7, 9, 11],
    'mixolydian':   [0, 2, 4, 5, 7, 9, 10],
    'aeolian':      [0, 2, 3, 5, 7, 8, 10],
    'locrian':      [0, 1, 3, 5, 6, 8, 10],

    'har_minor':    [0, 2, 3, 5, 7, 8, 11],
    'mel_minor':    [0, 2, 3, 5, 7, 9, 11],

    # Symmetrical Scales
    'chromatic':    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],

    # Pentatonic Modes
    '1st_pentatonic':   [0, 3, 5, 7, 10],
    '2nd_pentatonic':   [0, 2, 4, 7, 9],
    '3rd_pentatonic':   [0, 2, 5, 7, 10],
    '4th_pentatonic':   [0, 3, 5, 8, 10],
    '5th_pentatonic':   [0, 2, 5, 7, 9],

    'whole_tone': [0, 2, 4, 6, 8, 10]
}

# BPM sub-divisions
sub_divisions = {
    '1': 0.25,
    '2': 0.5,
    '3': 0.75,
    '4': 1,
    '6': 1.5,
    '8': 2,
    '12': 3,
    '16': 4
}

# Frequency bases in Hz
bases = {
    '1': 110,
    '2': 220,
    '3': 440
}
