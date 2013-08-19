"""
Defines the shape class, which is used to represent the geometric
shape of an entity
"""
import math

from pyglet.gl import *
import pyglet
import numpy as np

from vector import Vector, generate_axes, project, distance


class Shape(object):
    """Represents a closed geometric shape in 2D space

    Stores the vertices of the shape as wellas a list of indices.
    Also contains a draw method for drawing the shape to the screen,
    accounting for position, rotation, and scale.

    The vertices are stored as a tuple to ensure immutability of
    the vertices.

    Attributes:
        _verts: a tuple defining the vertices of the shape
        _num_verts: the number of vertices defining the shape
        _indices: the indices defining how to draw the shape
    """

    def __init__(self, verts, pos, rot, scale):
        """Creates a new drawable shape

        Args:
            verts: a tuple of numbers which define the vertices of
                   the shape (every 2 numbers makes up a vertex)
        Returns:
            a new Shape

        """
        self._verts = tuple(verts)
        self._num_verts = len(verts) // 2
        self._indices = self._gen_indices()
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.effective_length = self._get_effective_length()

    def _gen_indices(self):
        """Generates the indices for the shape
        Because the shape is closed, we want the indices to
        follow a pattern similar to [0, 1, 1, 2, 2, 0]. This
        method generates such a list.

        """
        indices = []

        # Generate the indices based on a pattern like
        # [0, 1, 1, 2, 2, 3, 3, 0]:
        # Add 0 to start, append two instances of i until
        # we hit num_verts, then end with another 0 to close
        # the shape
        indices.append(0)
        for i in range(1, self._num_verts):
            indices.extend([i, i])
        indices.append(0)

        return indices

    def collides(self, other):
        """Checks if this shape collides with another

        Args:
            other: the shape to test collision against
        Returns:
            True if the two shapes collide, False if they do not
        """
        # Start with a bounding circle test, using the effective
        # lengths as radii for the circles. If we don't at least
        # pass this, then the shapes don't collide, and we skip
        # doing the more computationally expensive collision test
        if distance(self.pos, other.pos) > (self.effective_length +
                                            other.effective_length):
            return False

        # We passed the bounding circle test, so we now need to do the
        # more accurate test for collision, using the separating axis
        # theorem

        # First grab the transformed (world-space) vertices of each
        # shape. Then, grab the axes, which are normalized vectors
        # perpendicular to each side
        verts1 = self._get_transformed_verts()
        verts2 = other._get_transformed_verts()
        axes1 = generate_axes(verts1)
        axes2 = generate_axes(verts2)

        # Loop over each set of axes, and project both shapes onto
        # each axis. If they don't overlap on the axis, the shapes do
        # not collide
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

    def _get_vectors(self):
        """Converts the tuple of vertex values for this shape
        into a list of vectors

        Returns:
            a list of vectors defining the shape
        """
        vectors = []

        # Every 2 values in the _verts list represents a vector.
        # This for loop turns each pair of verts into vectors
        for i in range(0, len(self._indices), 2):
            vectors.append(Vector(self._verts[i], self._verts[i + 1]))
        return vectors

    def _get_model_view(self):
        """Grabs the model view matrix based on the
        current state of the shape.

        Returns:
            the model view matrix for this shape
        """
        # Create the transformation matrices (scale, rotate, and
        # translate)
        scale = np.matrix([[self.scale, 0, 0, 0],
                           [0, self.scale, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])

        # We need the rotation in radians when using the cos/sin
        # functions
        theta = math.radians(self.rot)
        rot = np.matrix([[math.cos(theta), -math.sin(theta), 0, 0],
                         [math.sin(theta), math.cos(theta), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])

        translate = np.matrix([[1, 0, 0, self.pos.x],
                               [0, 1, 0, self.pos.y],
                               [0, 0, 1, 0],
                               [0, 0, 0, 1]])

        # Multiply out the matrices to get the model-view matrix
        mv = translate * rot * scale
        return mv

    def _get_transformed_verts(self):
        """Gets the transformed vertices of the shape

        Returns:
            the vertices of the object, in world-space
        """
        # Grab the model view matrix and the non-transformed
        # vertices of the objects as vectors
        mv = self._get_model_view()
        verts = self._get_vectors()

        # For each vertex, convert it to a matrix and then
        # multiply by the model-view matrix
        # Then, transform it back into a vector and store it in
        # the list
        transVerts = []
        for vert in verts:
            vert_m = vert.toMatrix()
            vert_t = mv * vert_m
            vec_t = Vector(vert_t[0, 0], vert_t[1, 0])
            transVerts.append(vec_t)

        return transVerts

    def _get_effective_length(self):
        """Gets the effective length of the shape

        The effective length can be thought of as a rough
        approximation of the length of the shape.

        Returns:
            the effective length of the shape
        """
        # The only transformation we need to consider is scale
        mv = np.matrix([[self.scale, 0, 0, 0],
                        [0, self.scale, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])

        # Now we get the properly scaled vertices and store them
        # in a list
        verts = self._get_vectors()
        transVerts = []
        for vert in verts:
            vert_m = vert.toMatrix()
            vert_t = mv * vert_m
            vec_t = Vector(vert_t[0, 0], vert_t[1, 0])
            transVerts.append(vec_t)

        # The distance of each vertex from the origin is just
        # the length of the vector defining it. We find the longest
        # length and use it as the approximate length of the shape
        # We also give it a little padding so the transition isn't so
        # sudden
        return 15 + max([vert.length() for vert in transVerts])

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
        pyglet.graphics.draw_indexed(self._num_verts, GL_LINES,
                                     self._indices, ('v2f', self._verts))
