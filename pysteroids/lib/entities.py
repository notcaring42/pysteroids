"""The base entity class and any non-player classes derived from it.
Defines all the objects in the game.
"""
import random as rand
import sys

import pyglet

from geometry.shape import Shape
from geometry.vector import Vector
from utils import WINDOW_WIDTH, WINDOW_HEIGHT, wrap_angle, rand_direction


class Entity(object):
    """Base class for defining an entity in the
       game (such as a ship, asteroid, etc.)

       The Entity class is a base class for all the objects in
       the game, including the player, the asteroids, and anything
       else. It is defined graphically by a shape. The class also
       stores the current position, rotation, and scale of the objects
       which are used when it is drawn to the screen, as well as a
       direction vector which defines where the entity is pointing.

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
        """Updates the entity's shape

        Args:
            dt: the amount of time since the last update
            window: the game window
        """
        # Move and rotate the entity
        self.pos += self._direction * self.lin_speed
        self.rot += self.rot_speed
        self.rot = wrap_angle(self.rot)

        # Set new values
        self._shape.update(self.pos, self.rot, self.scale)

        # Reflect across the screen, if necessary
        self._reflect_across_screen()

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

    def _reflect_across_screen(self):
        """Checks if the entity needs to be reflected across the
        screen and generates a new position if it does
        """
        # Start with the current position
        new_pos = Vector(self.pos.x, self.pos.y)

        # For each side of the screen, check if the entity has
        # exceeded the bounds using the approximate length

        # Check horizontal
        # Left-side
        if (self.pos.x + self._shape.effective_length < 0):
            dist = abs(0 - (self.pos.x + self._shape.effective_length))
            new_pos.x = WINDOW_WIDTH + dist
        # Right-side
        elif (self.pos.x - self._shape.effective_length > WINDOW_WIDTH):
            dist = abs((self.pos.x - self._shape.effective_length) -
                       WINDOW_WIDTH)
            new_pos.x = -dist

        # Check vertical
        # Bottom
        if (self.pos.y + self._shape.effective_length < 0):
            dist = abs(0 - (self.pos.y + self._shape.effective_length))
            new_pos.y = WINDOW_HEIGHT + dist
        # Top
        elif (self.pos.y - self._shape.effective_length > WINDOW_HEIGHT):
            dist = abs((self.pos.y - self._shape.effective_length) -
                       WINDOW_HEIGHT)
            new_pos.y = -dist

        # Set the new position of the entity.
        # If no reflection was needed, it's just the original position
        self.pos = new_pos

    # Direction stored as a property to ensure normalization
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value.normalize()


class Asteroid(Entity):
    """Defines an asteroid

    Asteroids only come in a discrete number of sizes and shapes.
    Size determines the scale and what the asteroid will break into
    when destroyed: a 'small' asteroid disappears, while larger
    asteroids break into smaller ones.

    Attributes:
        _shapes: a list of tuples with two elements,
                  element 0 is a tuple of vertices defining a shape
                  element 1 is the default scale of that shape
                  (the scale for a medium-sized asteroid with that
                  shape)
        max_lin_speed: the maximum linear speed an asteroid can have
        min_lin_speed: the minimum linear speed an asteroid can have
        max_rot_speed: the maximum rotational speed an asteroid
                       can have
        effect_player: the game's EffectPlayer
    """
    class Size:
        """Defines the possible asteroid sizes"""
        SMALL = 0   # Explodes
        MEDIUM = 1  # Breaks into 2 smalls
        LARGE = 2   # Breaks into 2 mediums
        HUGE = 3    # Breaks into 3 mediums

    _shapes = None
    max_lin_speed = 1.5
    max_rot_speed = 2.5
    min_lin_speed = 0.5

    @classmethod
    def _get_shapes(cls):
        """Retrieves the asteroids shapes defined in
        asteroids.txt and populates the shapes list
        with them"""

        # Ensure we actually have an asteroids.txt file to parse
        try:
            ast_file = pyglet.resource.file('asteroids.txt', 'r')
        except IOError:
            sys.exit('ERROR: res/asteroids.txt not found!')

        shapes = []

        for line in ast_file:
            # Each line of asteroids.txt is a list of numbers
            # with spaces in between each entry, so first
            # we split the line to turn that into a list
            verts = line.split(' ')

            # Next we convert each entry into a floating point
            # number
            for i in range(0, len(verts)):
                try:
                    verts[i] = float(verts[i])
                except ValueError:
                    sys.exit("""ERROR: found entry in asteroids.txt which is
                        not a number!""")

            # The last entry of each line is the default scale
            # (scale for a medium-sized asteroid with this shape)
            # Each entry in shapes is a tuple with entry 0 being
            # a tuple of the vertices of the shape, entry 1 being
            # the default scale
            shapes.append((tuple(verts[0:-1]), verts[-1]))

        cls._shapes = shapes

    def __init__(self, size, direction, lin_speed, rot_speed,
                 shape_index=None, pos=Vector(0, 0), rot=0.0):
        """Creates a new Asteroid

        Args:
            size: the size of the Asteroid, which should be a value
                  from Asteroid.Size
            shape_index: the index of the shape to grab from _shapes.
                         If None, then we'll grab a random one
            pos: the position of the asteroid
            rot: the rotation of the asteroid
        Returns:
            a new Asteroid
        """
        self.size = size

        # If we haven't grabbed the shapes from asteroids.txt, do so
        if Asteroid._shapes is None:
            self._get_shapes()

        # Two cases:
        # 1. a shape index wasn't supplied, generate a random one
        # (this is for newly generated asteroids)
        # 2. a shape index was supplied, use that (this is for
        # asteroids which resulted from the destruction of a larger
        # one)
        if shape_index is None:
            self.shape_index = rand.randrange(0, len(Asteroid._shapes))
        else:
            self.shape_index = shape_index

        # Get the relevant data from the tuple
        self._shape = Asteroid._shapes[self.shape_index][0]
        self._def_scale = Asteroid._shapes[self.shape_index][1]

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

        # Grab the EffectPlayer
        from effect import EffectPlayer
        self.effect_player = EffectPlayer.instance()

        Entity.__init__(self, self._shape, direction, lin_speed=lin_speed,
                        rot_speed=rot_speed, pos=pos, rot=rot,
                        scale=self._def_scale * scale_factor)

    def destroy(self):
        """Destroys an asteroid and breaks it into pieces
        (if applicable)

        Returns:
            a list containing the asteroids resulting from
            the destruction of this one
        """
        # Play destroy animation
        self.effect_player.play_animation('ASTEROID_DESTROY', self.pos)

        # Depending on the size of the asteroid, create
        # new asteroids resulting from its destruction
        if self.size == Asteroid.Size.SMALL:
            return []
        elif self.size == Asteroid.Size.MEDIUM:
            return [self._get_random_asteroid(Asteroid.Size.SMALL),
                    self._get_random_asteroid(Asteroid.Size.SMALL)]
        elif self.size == Asteroid.Size.LARGE:
            return [self._get_random_asteroid(Asteroid.Size.MEDIUM),
                    self._get_random_asteroid(Asteroid.Size.MEDIUM)]
        elif self.size == Asteroid.Size.HUGE:
            return [self._get_random_asteroid(Asteroid.Size.MEDIUM),
                    self._get_random_asteroid(Asteroid.Size.MEDIUM),
                    self._get_random_asteroid(Asteroid.Size.MEDIUM)]

    def _get_random_asteroid(self, size):
        """Creates a random asteroid that results from the destruction
        of this asteroid

        Parameters:
            size: the size that the new asteroid will have
        Returns:
            a new random asteroid, based on the characteristcs of
            this asteroid
        """
        # Generate random speeds
        lin_speed = rand.uniform(self.min_lin_speed, self.max_lin_speed)
        rot_speed = rand.uniform(0, self.max_rot_speed)

        # Get random direction
        direction = rand_direction(self.pos)

        return Asteroid(size, direction, lin_speed, rot_speed, pos=self.pos,
                        shape_index=self.shape_index)


class Bullet(Entity):
    """A bullet that is shot by the player and can destroy an asteroid

    Attributes:
        _lifespan: the amount of time, in seconds, that a bullet lasts
            before it is destroyed
        _current_lifespan: the current amount of time the bullet has
            existed on the screen
        expired: a boolean value representing whether the bullet's
            current amount of time in play has exceeded the lifespan
    """
    _lifespan = 1.6

    def __init__(self, pos, rot, direction):
        """Creates a new bullet

        Parameters:
            pos: the position of the bullet
            rot: the rotation of the bullet, in degrees
            direction: the direction of the bullet's movement

        Returns:
            a new Bullet
        """
        self.expired = False
        self._current_lifespan = 0

        Entity.__init__(self, (10, 10, 10, -10, -10, -10, -10, 10),
                        direction, pos=pos, rot=rot, lin_speed=3.0,
                        scale=0.25)

    def update(self, dt):
        """Updates this bullet's parameters, and checks
        the current lifespan of the bullet

        Parameters:
            dt: the time since the last update
        """
        # Update all of the Entity values
        Entity.update(self, dt)

        # Add the amount of time that has passed to the current
        # lifespan. If the current lifespan has exceeded the lifespan
        # of a bullet, flag the bullet has expired.
        self._current_lifespan += dt
        if self._current_lifespan >= self._lifespan:
            self.expired = True
