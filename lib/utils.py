from math import sqrt
import pyglet
from pyglet.gl import *


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

    def toTuple(self):
        """Converts the vector to a tuple representation

        Returns:
            a tuple representing the vector

        """
        return (self.x, self.y)

    def toList(self):
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
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        """Normalizes the vector, which will
        maintain the same direction but make the length 1

        """
        length = self.length()
        if length == 0.0:
            return
        # Note that length is a float, so we don't need a type conversion
        # even if x and y are ints
        self.x /= length
        self.y /= length

    def dot(self, other):
        """Returns the dot product of this vector and another

        Args:
            other: another vector
        Returns:
            the dot product of the two vectors

        """
        return (self.x * other.x) + (self.y * other.y)

    @staticmethod
    def Zero():
        """Gets an empty vector (0, 0)

        Returns:
            the zero vector (0, 0)
        """
        return Vector(0, 0)


class Shape(object):
    """Represents a closed geometric shape in 2D space

    Stores the vertices of the shape as wellas a list of indices.
    Also contains a draw method for drawing the shape to the screen,
    accounting for position, rotation, and scale.

    The vertices are stored as a tuple to ensure immutability of
    the vertices.

    Attributes:
        __verts: a tuple defining the vertices of the shape
        __num_verts: the number of vertices defining the shape
        __indices: the indices defining how to draw the shape

    """

    def __init__(self, verts):
        """Creates a new drawable shape

        Args:
            verts: a tuple of numbers which define the vertices of
                   the shape (every 2 numbers makes up a vertex)
        Returns:
            a new Shape

        """
        self.__verts = tuple(verts)
        self.__num_verts = len(verts) // 2
        self.__indices = self.__genIndices()

    def __genIndices(self):
        """Generates the indices for the shape
        Because the shape is closed, we want the indices to
        follow a pattern similar to [0, 1, 1, 2, 2, 0]. This
        method generates such a list.

        """
        indices = []

        # Generate the indices based on a pattern like
        # [0, 1, 1, 2, 2, 3, 3, 0]:
        # For i = 0 we just add 0 to start, and from there just append
        # two instances of i
        # For the last index, we also append an extra 0 to close the shape
        for i in range(0, self.__num_verts):
            if i == 0:
                indices.append(0)
            elif i == self.__num_verts - 1:
                indices.extend([i, i, 0])
            else:
                indices.extend([i, i])

        return indices

    def draw(self, pos, rot, scale):
        """Draws the shape onto the screen

        """
        # Start with the identity matrix and then load in
        # the transformation matrices
        glLoadIdentity()
        glTranslatef(pos.x, pos.y, 0.0)
        glRotatef(rot, 0, 0, 1)
        glScalef(scale, scale, scale)

        # Draw the lines that make up the shape
        # Use the 'v2f' format in case we're using vertices with floats
        pyglet.graphics.draw_indexed(self.__num_verts, GL_LINES,
                                     self.__indices, ('v2f', self.__verts))
