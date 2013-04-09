"""
Defines the shape class, which is used to represent the geometric
shape of an entity
"""
from pyglet.gl import *
import numpy as np
from vector import Vector, generate_axes, project


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

    def __init__(self, verts, pos, rot, scale):
        """Creates a new drawable shape

        Args:
            verts: a tuple of numbers which define the vertices of
                   the shape (every 2 numbers makes up a vertex)
        Returns:
            a new Shape

        """
        self.__verts = tuple(verts)
        self.__num_verts = len(verts) // 2
        self.__indices = self.__gen_indices()
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.effective_length = self.__get_effective_length()

    def __gen_indices(self):
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

    def collides(self, other):
        """Checks if this shape collides with another

        Args:
            other: the shape to test collision against
        Returns:
            True if the two shapes collide, False if they do not
        """
        # First grab the transformed (world-space) vertices of each shape
        # Then, grab the axes, which are normalized vectors perpendicular
        # to each side
        verts1 = self.__get_transformed_verts()
        verts2 = other.__get_transformed_verts()
        axes1 = generate_axes(verts1)
        axes2 = generate_axes(verts2)

        # Loop over each set of axes, and project both shapes onto each axis
        # If they don't overlap on the axis, the shapes do not collide
        for axis in axes1:
            proj1 = project(verts1, axis)
            proj2 = project(verts2, axis)

            if not proj1.overlaps(proj2):
                return False

        for axis in axes2:
            proj1 = project(verts1, axis)
            proj2 = project(verts2, axis)

            if not proj1.overlaps(proj2):
                return False

        # If we got this far, the shapes overlap on each axis,
        # and the shapes collide
        return True

    def __get_vectors(self):
        """Converts the tuple of vertex values for this shape
        into a list of vectors

        Returns:
            a list of vectors defining the shape
        """
        vectors = []

        # Every 2 values in the __verts list represents a vector.
        # This for loop turns each pair of verts into vectors
        for i in range(0, len(self.__indices), 2):
            vectors.append(Vector(self.__verts[i], self.__verts[i + 1]))
        return vectors

    def __get_model_view(self):
        """Grabs the model view matrix based on the
        current state of the shape.

        Returns:
            the model view matrix for this shape
        """
        # Use OpenGL commands to generate the model-view matrix,
        # based on position, rotation, and scale values
        glLoadIdentity()
        glTranslatef(self.pos.x, self.pos.y, 0.0)
        glRotatef(self.rot, 0, 0, 1)
        glScalef(self.scale, self.scale, self.scale)

        # Now we grab the model view matrix and store it in
        # an array of GLfloat's
        float_arr = (GLfloat * 16)()
        glGetFloatv(GL_MODELVIEW_MATRIX, float_arr)

        # The final step is to convert the array of floats into
        # a NumPy matrix. We convert the values to a list to
        # construct the matrix, and then resize it to a 4x4 matrix.
        # We need to take the transpose to get the matrix in the
        # correct orientation
        mv = np.matrix(list(float_arr))
        mv.resize((4, 4))
        mv = mv.transpose()
        return mv

    def __get_transformed_verts(self):
        """Gets the transformed vertices of the shape

        Returns:
            the vertices of the object, in world-space
        """
        # Grab the model view matrix and the non-transformed
        # vertices of the objects as vectors
        mv = self.__get_model_view()
        verts = self.__get_vectors()

        # For each vertex, convert it to a matrix and then
        # multiply by the model-view matrix
        # Then, transform it back into a vector and store it in
        # the list
        transVerts = []
        for vert in verts:
            v_m = vert.toMatrix()
            v_m = mv * v_m
            v_t = Vector(v_m[0, 0], v_m[1, 0])
            transVerts.append(v_t)

        return transVerts

    def __get_effective_length(self):
        """Gets the effective length of the shape

        The effective length can be thought of as a rough
        approximation of the length of the shape.

        Returns:
            the effective length of the shape
        """
        # First we need to load up the model view matrix.
        # We only care about the shape in reference to the origin,
        # and rotation won't be considered, so the position and
        # rotation values aren't applied.
        # However, we do need the scale value to get a somewhat
        # accurate approximation
        glLoadIdentity()
        glScalef(self.scale, self.scale, self.scale)

        # Now we grab the model view matrix and store it in
        # an array of GLfloat's
        float_arr = (GLfloat * 16)()
        glGetFloatv(GL_MODELVIEW_MATRIX, float_arr)

        # The final step is to convert the array of floats into
        # a NumPy matrix. We convert the values to a list to
        # construct the matrix, and then resize it to a 4x4 matrix.
        # We need to take the transpose to get the matrix in the
        # correct orientation
        mv = np.matrix(list(float_arr))
        mv.resize((4, 4))
        mv = mv.transpose()

        # Now we get the properly scaled vertices and store them
        # in a list
        verts = self.__get_vectors()
        transVerts = []
        for vert in verts:
            v_m = vert.toMatrix()
            v_m = mv * v_m
            v_t = Vector(v_m[0, 0], v_m[1, 0])
            transVerts.append(v_t)

        # The distance of each vertex from the origin is just
        # the length of the vector defining it. We find the longest
        # length and use it as the approximate length of the shape
        # We also give it a little padding so the transition isn't so
        # sudden
        return 20 + max([vert.length() for vert in transVerts])

    def update(self, pos, rot, scale):
        self.pos = pos
        self.rot = rot
        self.scale = scale

    def draw(self):
        """Draws the shape onto the screen"""
        # Start with the identity matrix and then load in
        # the transformation matrices
        glLoadIdentity()
        glTranslatef(self.pos.x, self.pos.y, 0.0)
        glRotatef(self.rot, 0, 0, 1)
        glScalef(self.scale, self.scale, self.scale)

        # Draw the lines that make up the shape
        # Use the 'v2f' format in case we're using vertices with floats
        pyglet.graphics.draw_indexed(self.__num_verts, GL_LINES,
                                     self.__indices, ('v2f', self.__verts))
