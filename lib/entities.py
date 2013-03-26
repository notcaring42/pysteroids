"""
The base entity class and any classes derived from it.
Defines all the objects in the game.
"""
from utils import Shape, Vector, clamp
from math import sin, cos, radians
from pyglet.window import key
from random import randrange


class Entity(object):
    """Base class for defining an entity in the
       game (such as a ship, asteroid, etc.)

       The Entity class is a base class for all the objects in
       the game, including the player, the asteroids, and anything else.
       It is defined graphically by a shape. The class also stores the
       current position, rotation, and scale of the objects which are
       used when it is drawn to the screen, as well as a direction vector
       which defines where the entity is pointing.

       Attributes:
            _shape: the shape graphically defining the entity
            pos: the position of the entity
            rot: the rotation of the entity (in degrees)
            scale: the scale of the entity
            lin_speed: the linear speed of the entity
            rot_speed: the rotational speed of the entity
            _direction: the direction of the entity (used for movement)

    """
    def __init__(self, verts, direction, lin_speed=0.0, rot_speed=0.0,
                 pos=Vector(0, 0), rot=0.0, scale=1.0):
        """Creates a new Entity

        Args:
            verts: the vertices defining the shape of the entity
            direction: the direction of the entity
            lin_speed: the linear speed of the entity
            rot_speed: the rotational speed of the entity
            pos: the position of the entity
            rot: the rotation of the entity (in degrees)
            scale: the scale of the entity
        Returns:
            a new Entity

        """
        self._shape = Shape(verts, pos, rot, scale)
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.lin_speed = lin_speed
        self.rot_speed = rot_speed
        self._direction = direction.normalize()

    def update(self, dt):
        """Updates the ship's position

        Args:
            dt: the amount of time since the last update
        """
        # Move and rotate the entity
        self.pos += self._direction * self.lin_speed
        self.rot += self.rot_speed

        # Set new values
        self._shape.pos = self.pos
        self._shape.rot = self.rot
        self._shape.scale = self.scale

    def draw(self):
        """Draws the entity onto the screen

        """
        # Defer this to the shape
        self._shape.draw()

    def collides(self, other):
        """Checks whether this entity collides with another one

        Args:
            other: the other entity to test collision with
        Returns:
            True if the entities collide, False if they do not
        """
        return self._shape.collides(other._shape)

    # Direction stored as a property to ensure normalization
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value.normalize()


class Ship(Entity):
    """Defines the player's ship.

    An extension of the entity class, but with a self-defined shape and
    input handling.

    Attributes:
        __max_speed: the maximum units per update that the ship can travel
        __movement: the movement vector that the ship is translated by
                    each frame
    """

    __max_speed = 1.5

    def __init__(self, pos=Vector(0, 0), rot=0.0):
        """Creates a new Ship

        Args:
            pos: the position of the ship
            rot: the rotation of the ship

        Returns:
            a new Ship instance
        """

        # Get the initial direction of the ship using the rotation
        direction = Vector(cos(radians(rot)), sin(radians(rot)))

        # Initially, the ship isn't moving
        self.__movement = Vector.Zero()

        Entity.__init__(self, (30, 0, -30, 20, -30, -20), direction,
                        1.0, 1.0, pos, rot, 0.5)

    def __handle_input(self, keys, dt):
        """Handles any input from the player.

        Args:
            keys: the keyboard state
            dt: the amount of time since the last update
        """

        # Moves the ship forward
        #
        # Moving works like this: each frame the ship is translated
        # by the movement vector. When the ship moves forward, a scalar
        # multiple of the direction vector is added to the movement vector
        # This simulates zero-gravity movement for the ship: even if
        # the player is facing a different direction, the movement
        # still continues in the same direction until thrusters are engaged
        if keys[key.W]:
            self.__movement += self._direction * self.lin_speed * dt

        # Set a maximum speed
        # Normalize the movement vector and then multiply
        # by the new length to get the new speed
        new_length = clamp(self.__movement.length(),
                           -self.__max_speed, self.__max_speed)
        self.__movement = self.__movement.normalize()
        self.__movement *= new_length

        # Rotate the ship
        if keys[key.A]:
            self.rot += self.rot_speed
        elif keys[key.D]:
            self.rot -= self.rot_speed

    def update(self, keys, dt):
        """Updates the ship and handles input

        Args:
            keys: the keyboard state
            dt: the amount of time since the last update
        """
        # Move the ship
        self.__handle_input(keys, dt)
        self.pos += self.__movement

        # Update variables
        self._shape.pos = self.pos
        self._shape.rot = self.rot
        self._shape.scale = self.scale

    # Direction stored as a property to ensure normalization
    @property
    def direction(self):
        return self._direction

    # Setting the rotation of the ship also sets the new direction
    @property
    def rot(self):
        return self.__rot

    @rot.setter
    def rot(self, value):
        self.__rot = value

        # Set new direction vector
        self._direction = Vector(cos(radians(value)), sin(radians(value)))


class Asteroid(Entity):
    """Defines an asteroid

    Asteroids only come in a discrete number of sizes and shapes.
    Size determines the scale and what the asteroid will break into
    when destroyed: a 'small' asteroid disappears, while larger
    asteroids break into smaller ones.

    Attributes:
        __shapes: a list of tuples with two elements,
                  element 0 is a tuple of vertices defining a shape
                  element 1 is the default scale of that shape
                  (the scale for a medium-sized asteroid with that shape)
    """
    class Size:
        """Defines the possible asteroid sizes"""
        SMALL = 0   # Explodes
        MEDIUM = 1  # Breaks into 2 smalls
        LARGE = 2   # Breaks into 2 mediums
        HUGE = 3    # Breaks into 3 mediums

    __shapes = None

    @classmethod
    def __get_shapes(cls):
        """Retrieves the asteroids shapes defined in
        asteroids.txt and populates the shapes list
        with them"""

        ast_file = open('res/asteroids.txt', 'r')
        shapes = []

        for line in ast_file:
            # Each line of asteroids.txt is a list of numbers
            # with spaces in between each entry, so first
            # we split the line to turn that into a list
            verts = line.split(' ')

            # Next we convert each entry into a floating point
            # number
            for i in range(0, len(verts)):
                verts[i] = float(verts[i])

            # The last entry of each line is the default scale
            # (scale for a medium-sized asteroid with this shape)
            # Each entry in shapes is a tuple with entry-0 being
            # a tuple of the vertices of the shape, and entry-1 being
            # the default scale
            shapes.append((tuple(verts[0:-1]), verts[-1]))

        cls.__shapes = shapes

    def __init__(self, size, shape_index=None,
                 pos=Vector(0, 0), rot=0.0):
        """Creates a new Asteroid

        Args:
            size: the size of the Asteroid, which should be a value
                  from Asteroid.Size
            shape_index: the index of the shape to grab from __shapes.
                         If None, then we'll grab a random one
            pos: the position of the asteroid
            rot: the rotation of the asteroid
        Returns:
            a new Asteroid
        """
        self.size = size

        # If we haven't grabbed the shapes from asteroids.txt, do so
        if Asteroid.__shapes is None:
            self.__get_shapes()

        # Two cases:
        # 1. a shape index wasn't supplied, generate a random one (this is
        # for newly generated asteroids)
        # 2. a shape index was supplied, use that (this is for asteroids which
        # resulted from the destruction of a larger one)
        if shape_index is None:
            self.shape_index = randrange(0, len(Asteroid.__shapes))
        else:
            self.shape_index = shape_index

        # Get the relevant data from the tuple
        self.__shape = Asteroid.__shapes[self.shape_index][0]
        self.__def_scale = Asteroid.__shapes[self.shape_index][1]

        # For each size, we apply a scaling factor on top of the
        # default scale to make smaller asteroids smaller and larger
        # asteroids larger
        # As with the definition of default scale, a medium sized
        # asteroid just uses the default scale (scale_factor = 1.0)
        if size == Asteroid.Size.SMALL:
            scale_factor = 0.7
        elif size == Asteroid.Size.MEDIUM:
            scale_factor = 1.0
        elif size == Asteroid.Size.LARGE:
            scale_factor = 1.2
        elif size == Asteroid.Size.HUGE:
            scale_factor = 1.5

        Entity.__init__(self, self.__shape, Vector(0, 0),
                        pos=pos, rot=rot, scale=self.__def_scale * scale_factor)

    def destroy(self):
        """Destroys an asteroid and breaks it into pieces
        (if applicable)

        Returns:
            a list containing the asteroids resulting from
            the destruction of this one
        """
        # From the definitions given in Asteroid.Size
        if self.size == Asteroid.Size.SMALL:
            return []
        elif self.size == Asteroid.Size.MEDIUM:
            return [Asteroid(Asteroid.Size.SMALL, pos=self.pos,
                             shape_index=self.shape_index),
                    Asteroid(Asteroid.Size.SMALL, pos=self.pos,
                             shape_index=self.shape_index)]
        elif self.size == Asteroid.Size.LARGE:
            return [Asteroid(Asteroid.Size.MEDIUM, pos=self.pos,
                             shape_index=self.shape_index),
                    Asteroid(Asteroid.Size.MEDIUM, pos=self.pos,
                             shape_index=self.shape_index)]
        elif self.size == Asteroid.Size.HUGE:
            return [Asteroid(Asteroid.Size.MEDIUM, pos=self.pos,
                             shape_index=self.shape_index),
                    Asteroid(Asteroid.Size.MEDIUM, pos=self.pos,
                             shape_index=self.shape_index),
                    Asteroid(Asteroid.Size.MEDIUM, pos=self.pos,
                             shape_index=self.shape_index)]
