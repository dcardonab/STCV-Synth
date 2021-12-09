from math import acos, asin, atan2, degrees, sqrt
from typing import Tuple, Union

"""
MATH FUNCTIONS
"""
# Magnitude is the square root of the sum of the powers of the list items
# *args allows declaring a variable number of arguments.
def magnitude(*args: float) -> float:
    return sqrt(sum(arg ** 2 for arg in args))


# Normalize a variable size vector
# Returns a tuple containing each normalized argument
def normalize(*args: float) -> float:
    norm = magnitude(*args)
    try:
        return tuple(arg / norm for arg in args)
    except ZeroDivisionError:
        print("Attempted to divide by 0 when normalizing. \
            Waiting for next set of quaternions.")
        return tuple(arg for arg in args)


# Function to set a range of values to another range of values.
def scale(val: float,
          src: Tuple[float, float],
          dst: Tuple[float, float]) -> float:
    return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

"""
EULER ANGLES
"""
# Roll is the rotation about the x axis
# Pitch is the rotation about the y axis
# Yaw is the rotation about the z axis

# Calculate the Euler Angles from a vector quaternion.
# In a relative quaternion, the initial value of the W (real) component
# is 1. The information received from the ST is a vector quaternion.
def vecQ_to_euler(i: float, j: float, k: float) -> Tuple[float, float, float]:
    w = 1
    # Normalize vector quaternion to set components in range for
    # inverse trigonometric function
    i, j, k = normalize(i, j, k)
    return roll_from_quaternion(w, i, j, k), \
           pitch_from_quaternion(w, i, j, k), \
           yaw_from_quaternion(w, i, j, k)


def pitch_from_quaternion(w: float, i: float, j: float, k: float) -> float:
    pitch = 2 * (w * j - i * k)
    # The following conditions prevent passing a value outside the arcsine
    # input range, which is -1 to 1 inclusive.
    if pitch > 1:
        pitch = degrees(asin(1))
    elif pitch < -1:
        pitch = degrees(asin(-1))
    else:
        pitch = degrees(asin(pitch))

    return round(pitch, 2)


def roll_from_quaternion(w: float, i: float, j: float, k: float) -> float:
    roll = degrees(atan2(2 * (w * i + j * k), 1 - 2 * (i ** 2 + j ** 2)))
    return round(roll, 2)


def yaw_from_quaternion(w: float, i: float, j: float, k: float) -> float:
    yaw = degrees(atan2(2 * (w * k + i * j), 1 - 2 * (j ** 2 + k ** 2)))
    return round(yaw, 2)


def orientation_from_acceleration(x: float, y: float, z: float) \
    -> Tuple[float, float, float]:
    # Magnitude
    r = round(magnitude(x, y, z), 2)
    # Inclination, which is also the pitch
    theta = round(degrees(acos(z / r)), 2)
    # Azimuth, which is also the roll
    phi = round(degrees(atan2(y, x)), 2)
    return r, theta, phi
