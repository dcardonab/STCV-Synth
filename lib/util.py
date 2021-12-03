from math import asin, atan2, degrees, sqrt


# Magnitude is the square root of the sum of the powers of the list items
def magnitude(values_list):
    return sqrt(sum(i ** 2 for i in values_list))

####################
### EULER ANGLES ###
####################

# All Euler angles are using an assumed value of 0 for the W (real) component,
# as the information received from the ST is a vector quaternion.

# Pitch is the rotations about the y axis (between -90 and 90 deg)
def pitch(i, j, k):
    w = 0
    return degrees(asin(2 * (w * j - i * k)))

# Roll is the rotation about the x axis (between -180 and 180 deg)
def roll(i, j, k):
    w = 0
    return degrees(atan2(2 * (w * i + j * k), 1 - 2 * (i ** 2 + j ** 2)))

# Yaw is the rotation about the z axis (between -180 and 180)
def yaw(i, j, k):
    w = 0
    return degrees(atan2(2 * (w * k + i * j), 1 - 2 * (j ** 2 + k ** 2)))
