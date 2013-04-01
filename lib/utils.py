"""
General utility functions and vectors
"""
window_width = 640
window_height = 480


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
