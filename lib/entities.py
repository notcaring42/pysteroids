from utils import Vector
from math import sin, cos, radians

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

    """
    def __init__(self, shape, pos=Vector(0, 0), rot=0.0, scale=1.0):
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
        self.__shape = shape
        self.pos = pos
        self.__rot = rot
        self.scale = scale
        self.__direction = Vector(cos(radians(rot)), sin(radians(rot)))

    def draw(self):
        """Draws the entity onto the screen

        """
        # Defer this to the shape
        self.__shape.draw(self.pos, self.rot, self.scale)

    # Direction stored as a property to ensure normalization
    @property
    def direction(self):
        return self.__direction

    @property
    def rot(self):
        return self.__rot

    @rot.setter
    def rot(self, value):
        self.__rot = value

        # Set new direction vector
        self.__direction = Vector(cos(radians(value)), sin(radians(value)))
