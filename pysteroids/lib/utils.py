"""General utility functions and classes"""
import random as rand

from geometry.vector import Vector

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


def rand_point():
    """Grabs a random point in the window

    Returns:
        a Vector representing the point that was chosen
    """
    rand_x = rand.randrange(0, WINDOW_WIDTH)
    rand_y = rand.randrange(0, WINDOW_HEIGHT)
    return Vector(rand_x, rand_y)


def rand_direction(pos):
    """Gets a random direction on the screen, relative to a given point

    Parameters:
        pos: the point from which the direction will be generated

    Returns:
        a normalized Vector representing a direction
    """
    return (rand_point() - pos).normalize()


def weighted_choice(choices):
    """Makes a random choice from a list, using weights to determine
    the probability of a certain choice being picked.

    Parameters:
        choices: a list of tuples, with the first entry being the
            choice, and the second entry being the weight of that
            choice

    Returns:
        a random choice from the list
    """
    # Grab the total of all the weights, and take a random number
    # between 0 and the total
    total = sum(weight for c, weight in choices)
    r = rand.uniform(0, total)

    # Iterate through the list, adding the weight to a variable called
    # 'upto'. If the number we're 'upto' plus the weight we're on
    # exceeds r, then choose that element. Otherwise, add the weight
    # to 'upto'
    upto = 0
    for choice, weight in choices:
        if upto + weight > r:
            return choice
        upto += weight

    # In case something goes wrong
    assert False, 'Nothing was chosen'


class Singleton(object):
    """Implementation of a Singleton design pattern, taken from
    http://stackoverflow.com/questions/42558/python-and-the-
    singleton-pattern

    Used as a decorator on a class to mark it as a singleton.
    The class can have an __init__ method with only 'self' as the
    argument. The instance for that class must be accesed through
    'instance()'

    Attributes:
        _decorated: the singleton class
        _instance: the sole instance of the singleton class
    """
    def __init__(self, decorated):
        """Marks a class as a singleton

        Parameters:
            decorated: the class marked with the @Singleton decorator
        """
        self._decorated = decorated

    def instance(self):
        """Returns the sole instance of the singleton class"""
        # Check to make sure the instance exists
        try:
            return self._instance
        # If not, we need to construct it
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        # Singletons can't have more than one instance
        raise TypeError('Singletons must be accesed through \'instance()\'')

    def __instancecheck__(self, inst):
        return isinstance(self, self._decorated)
