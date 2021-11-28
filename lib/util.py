from math import atan, pi, sqrt, radians

# REF:
#   https://engineering.stackexchange.com/questions/3348/calculating-pitch-yaw-and-roll-from-mag-acc-and-gyro-data


# This definition is temporal and it will be abstracted to the ST firmware.
def magnitude(values_list):
    [print(v) for v in values_list]
    mag = 0
    for v in values_list:
        mag += pow(v, 2)

    print(sqrt(mag))
    return sqrt(mag)

# Pitch is the rotations about the y axis (between -90 and 90 deg)
def pitch(x, y, z):
    pass

# Roll is the rotation about the x axis (between -180 and 180 deg)
def roll(x, y, z):
    pass

# Yaw is the rotation about the z axis (between -180 and 180)
def yaw(x, y, z):
    pass