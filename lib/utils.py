"""
General utility functions and classes
"""
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480


def clamp(x, low, high):
    """Clamps a number between two numbers

    Args:
        x: the number to clamp
        low: the minimum value the number can have
        high: the maximum value the number can have
    Returns:
        the value of x clamped between low and high
    """
    if x < low:
        return low
    elif x > high:
        return high
    else:
        return x


def wrap_angle(x):
    """Wraps an angle between 0 and 360 degrees

    Args:
        x: the angle to wrap
    Returns:
        a new angle on the interval [0, 360]
    """
    if x < 0:
        x = 360 - x
    elif x > 360:
        x = x - 360
    return x
