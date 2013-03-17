from utils import Shape, Vector, clamp
from math import sin, cos, radians
from pyglet.window import key


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
            __shape: the shape defining the entity, used for drawing
            pos: the position of the entity
            rot: the rotation (in degrees) of the entity.
                 When rot is set, the direction is adjusted as well
            __rot: private storage of the rotation
            scale: the scale of the entity
            direction: a Vector defining where the entity is pointing.
                       Get-only, because it is set when rot is set
            __direction: private storage of the direction vector
            movement: the movement vector by which the ship moves every frame

    """
    def __init__(self, verts, pos=Vector(0, 0), rot=0.0, scale=1.0):
        """Creates a new Entity

        Args:
            shape: the shape defining the entity geometrically
                   NOTE: ensure that you define the vertices such
                   that the front of the object lies along the x-axis
            pos: the position of the entity
            rot: the rotation of the entity, in degrees
            scale: the scale of the entity
        Returns:
            a new Entity

        """
        self.__shape = Shape(verts, pos, rot, scale)
        self.pos = pos
        self.__rot = rot
        self.scale = scale
        self.__direction = Vector(cos(radians(rot)), sin(radians(rot)))
        self.movement = Vector.Zero()

    def update(self, dt):
        """Updates the ship's position

        Args:
            dt: the amount of time since the last update
        """
        # Move the ship by the movement vector
        self.pos += self.movement
        self.__shape.pos = self.pos
        self.__shape.rot = self.rot
        self.__shape.scale = self.scale

    def draw(self):
        """Draws the entity onto the screen

        """
        # Defer this to the shape
        self.__shape.draw()

    def collides(self, other):
        """Checks whether this entity collides with another one

        Args:
            other: the other entity to test collision with
        Returns:
            True if the entities collide, False if they do not
        """

        # FOR DEBUG ONLY
        # In the case other is a Shape
        if isinstance(other, Shape):
            return self.__shape.collides(other)

        return self.__shape.collides(other.__shape)

    # Direction stored as a property to ensure normalization
    @property
    def direction(self):
        return self.__direction

    # Setting the rotation of the ship also sets the new direction
    @property
    def rot(self):
        return self.__rot

    @rot.setter
    def rot(self, value):
        self.__rot = value

        # Set new direction vector
        self.__direction = Vector(cos(radians(value)), sin(radians(value)))


class Ship(Entity):
    """Defines the player's ship.

    An extension of the entity class, but with a self-defined shape and
    input handling.

    Attributes:
        __keys: represents the current keyboard state for input handling
        __maxSpeed: the maximum units per update that the ship can travel
        __rotSpeed: the degrees per update that the ship rotates
    """

    __maxSpeed = 1.5
    __rotSpeed = 1.0

    def __init__(self, keys, pos=Vector(0, 0), rot=0.0, scale=0.5):
        """Creates a new Ship

        Args:
            keys: the keyboard state
            pos: the position of the ship
            rot: the rotation of the ship
            scale: the scaling factor to apply to the ship

        Returns:
            a new Ship instance
        """
        Entity.__init__(self, (30, 0, -30, 20, -30, -20),
                        pos, rot, scale)
        self.__keys = keys

    def __handleInput(self, dt):
        """Handles any input from the player.

        Args:
            dt: the amount of time since the last update
        """

        # Moves the ship forward
        if self.__keys[key.W]:
            self.movement += self.direction * dt

        # Set a maximum speed
        newLength = clamp(self.movement.length(),
                          -self.__maxSpeed, self.__maxSpeed)
        self.movement.normalize()
        self.movement *= newLength

        if self.__keys[key.A]:
            self.rot += self.__rotSpeed
        elif self.__keys[key.D]:
            self.rot -= self.__rotSpeed

    def update(self, dt):
        """Updates the ship and handles input

        Args:
            dt: the amount of time since the last update
        """
        self.__handleInput(dt)
        Entity.update(self, dt)
