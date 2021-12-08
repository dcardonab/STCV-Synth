from math import asin, atan2, degrees, sqrt


# Magnitude is the square root of the sum of the powers of the list items
# *args allows declaring a variable number of arguments.
def magnitude(*args):
    return sqrt(sum(arg ** 2 for arg in args))


# Normalize a variable size vector
# Returns a tuple containing each normalized argument
def normalize(*args):
    norm = magnitude(*args)
    try:
        return tuple(arg / norm for arg in args)
    except ZeroDivisionError:
        print("Attempted to divide by 0 when normalizing. \
            Waiting for next set of quaternions.")
        return tuple(arg for arg in args)


####################
### EULER ANGLES ###
####################

# Calculate the Euler Angles from a vector quaternion.
# The assumed value of the W (real) component is 0
# as the information received from the ST is a vector quaternion.
def vecQ_to_euler(i, j, k):
    w = 1
    # Normalize vector quaternion to set components in range for
    # inverse trigonometric function
    i, j, k = normalize(i, j, k)
    return roll(w, i, j, k), pitch(w, i, j, k), yaw(w, i, j, k)


# Pitch is the rotations about the y axis (between -90 and 90 deg)
def pitch(w, i, j, k):
    value = 2 * (w * j - i * k)
    # The following conditions prevent passing a value outside the arcsine
    # input range, which is -1 to 1 inclusive.
    if value > 1:
        return degrees(asin(1))
    elif value < -1:
        return degrees(asin(-1))
    else:
        return degrees(asin(value))


# Roll is the rotation about the x axis (between -180 and 180 deg)
def roll(w, i, j, k):
    return degrees(atan2(2 * (w * i + j * k), 1 - 2 * (i ** 2 + j ** 2)))


# Yaw is the rotation about the z axis (between -180 and 180)
def yaw(w, i, j, k):
    return degrees(atan2(2 * (w * k + i * j), 1 - 2 * (j ** 2 + k ** 2)))
