"""
Classes and functions for manipulating vectors and
projections
"""
from math import sqrt

import numpy as np


def distance(v1, v2):
    """Gets the distance between two vectors

    Parameters:
        v1, v2: vectors

    Returns:
        the distance between v1 and v2
    """
    return sqrt((v2.x - v1.x)**2 + (v2.y - v1.y)**2)


def project(verts, axis):
    """Projects a shape onto an axis

    Args:
        verts: the vertices defining the shape
        axis: the axis to project the shape onto
    Returns:
        the projection of the shape onto the axis
    """
    # v_min and v_max represent the minimum and maximum
    # values of the projection
    # Start with the projection value for the first vertex
    v_min = axis.dot(verts[0])
    v_max = v_min

    # Loop over the rest of the vertices and
    # find the projection values for each
    for i in range(1, len(verts)):
        p = axis.dot(verts[i])

        # Set the new minimum or maximum, if applicable
        if p < v_min:
            v_min = p
        elif p > v_max:
            v_max = p

    return Projection(v_min, v_max)


def generate_axes(verts):
    """Generates a list of perpendicular axes for a shape

    Args:
        verts: the vertices making up the shape
    Returns:
        a list of normalized axes perpendicular to the sides
        of the shape
    """
    axes = []

    # Generate vectors for each pair of vertices
    # representing the sides
    for i in range(0, len(verts)):
        p1 = verts[i]
        if (i + 1 == len(verts)):
            p2 = verts[0]
        else:
            p2 = verts[i + 1]

        edge = p1 - p2

        # Create the vector perpendicular to the side
        # and normalize it
        normal = Vector(edge.y, -edge.x)
        normal = normal.normalize()
        axes.append(normal)
    return axes


class Vector(object):
    """Represents a vector in 2D space

    Can hold integers or floats, and supports mathematically
    valid vector operations, such as addition/subtraction, as
    well as multiplication by a scalar.

    Attributes:
        x: x component of the vector
        y: y component of the vector
    """
    def __init__(self, x, y):
        """Creates a new vector

        Args:
            x: x component of the new vector
            y: y component of the new vector
        Returns:
            a new vector (x, y)

        """
        self.x = x
        self.y = y

    @staticmethod
    def from_tuple(tup):
        return Vector(tup[0], tup[1])

    def __add__(self, other):
        """Adds two vectors component-wise

        Args:
            other: The vector to add to this one
        Returns:
            a new vector representing the sum of
            'self' and 'other'
        Raises:
            TypeError: if 'other' is not a vector

        """
        newX = self.x + other.x
        newY = self.y + other.y
        return Vector(newX, newY)

    def __sub__(self, other):
        """Subtracts two vectors component-wise

        Args:
            other: The vector to subtract from this one
        Returns:
            a new vector representing the subtractions of
            'other' from 'self'
        Raises:
            TypeError: if 'other' is not a vector

        """
        newX = self.x - other.x
        newY = self.y - other.y
        return Vector(newX, newY)

    def __mul__(self, k):
        """Multiplies the vector by a scalar

        Args:
            k: the scalar to multiply the vector by
        Returns:
            a new vector representing 'self' multiplied
            by a scalar k
        Raises:
            TypeError: if k is not a number

        """
        # Ensure that k is a number
        if (isinstance(k, int) or isinstance(k, float)):
            newX = self.x * k
            newY = self.y * k
            return Vector(newX, newY)
        else:
            raise TypeError("unsupported operand type(s)" +
                            "for +: '{}' and '{}'".format(self.__class__,
                                                          type(k)))

    def __rmul__(self, k):
        """Multiplies the vector by a scalar

        Args:
            k: the scalar to multiply the vector by
        Returns:
            a new vector representing 'self' multiplied
            by a scalar k
        Raises:
            TypeError: if k is not a number

        """
        return self.__mul__(k)

    def __repr__(self):
        """Converts the vector to a string representation

        Returns:
            a string representation of the vector

        """
        return '(' + str(self.x) + ', ' + str(self.y) + ')'

    def __str__(self):
        """Converts the vector to a string representation

        Returns:
            a string representation of the vector

        """
        return '(' + str(self.x) + ', ' + str(self.y) + ')'

    def to_tuple(self):
        """Converts the vector to a tuple representation

        Returns:
            a tuple representing the vector

        """
        return (self.x, self.y)

    def to_list(self):
        """Converts the vector to a list representation

        Returns:
            a list representing the vector

        """
        return [self.x, self.y]

    def length(self):
        """Gets the length of the vector

        Returns:
            the length of the vector

        """
        return sqrt(self.x**2 + self.y**2)

    def normalize(self):
        """Returns a normalized version of this vector,
        which maintains the same direction but has length 1

        Returns:
            a normalized vector pointing in the same direction
            as this one
        """
        length = self.length()
        if length == 0.0:
            return self

        # Note that length is a float, so we don't need a type
        # conversion even if x and y are ints
        new_x = self.x / length
        new_y = self.y / length
        return Vector(new_x, new_y)

    def dot(self, other):
        """Returns the dot product of this vector and another

        Args:
            other: another vector
        Returns:
            the dot product of the two vectors

        """
        return (self.x*other.x) + (self.y*other.y)

    @staticmethod
    def zero():
        """Gets an empty vector (0, 0)

        Returns:
            the zero vector (0, 0)
        """
        return Vector(0, 0)

    def toMatrix(self):
        """Returns this vector represented as a numpy matrix

        Returns:
            a numpy matrix representing this vector, with
            a zeroed out z-component and an extra component
            to represent as a homogeneous coordinate
        """
        return np.matrix([[self.x], [self.y], [0], [1]])


class Projection(object):
    """Represents a 1-dimensional projection onto an axis, with
    a minimum and maximum value to represent it

    Attributes:
        minimum: the low-value of the projection
        maximum: the high-value of the projection
    """
    def __init__(self, minimum, maximum):
        """Creates a new Projection

        Args:
            minimum: the low-value of the projection
            maximum: the high-value of the projection
        Returns:
            a new Projection
        """
        self.minimum = minimum
        self.maximum = maximum

    def overlaps(self, other):
        """Checks if this projection overlaps another

        Args:
            other: the other projection to check for overlap
        Returns:
            True if the two projections overlap, False if they do not
        """
        return (self.minimum <= other.maximum) and \
               (other.minimum <= self.maximum)
