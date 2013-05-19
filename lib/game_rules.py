"""Contains classes for managing game rules"""
import random as rand

from lib.entities import Asteroid
from lib.geometry.vector import Vector
from lib.utils import weighted_choice, WINDOW_WIDTH, \
    WINDOW_HEIGHT, rand_direction


class AsteroidManager(object):
    """Uses game rules to generate asteroids

    Attributes:
        asteroids: list of currently active asteroids
        asteroid_count: the number of GENERATED asteroids in play
        game_rules: the currently active game rules used to generate
            asteroids
        next_gen_time: the time until the next asteroid will be
            generated
        last_gen_time: the time since the last asteroid was generated
    """
    def __init__(self, game_rules):
        """Creates a new AsteroidManager

        Parameters:
            game_rules: the game rules to use for generating asteroids
        Returns:
            a new AsteroidManager
        """
        self.asteroids = []
        self.asteroid_count = 0
        self.game_rules = game_rules
        self.next_gen_time = 0
        self.last_gen_time = 0

    def __gen_asteroid(self):
        """Generates a new asteroid

        Returns:
            a new, randomly generated asteroid
        """
        # Get a random size, with probability depending on the game
        # rules
        size = weighted_choice(self.game_rules.size_weights)

        # Generate a position out of bounds, and a random direction
        # to move towards
        possible_x = range(-60, -10, 10) + range(WINDOW_WIDTH+20,
                                                 WINDOW_WIDTH+70, 10)
        possible_y = range(-60, -10, 10) + range(WINDOW_HEIGHT+20,
                                                 WINDOW_HEIGHT+70, 10)
        pos = Vector(rand.choice(possible_x), rand.choice(possible_y))
        direction = rand_direction(pos)

        # Generate random linear and rotational speeds
        lin_speed = rand.uniform(Asteroid.min_lin_speed,
                                 Asteroid.max_lin_speed)
        rot_speed = rand.uniform(0, Asteroid.max_rot_speed)

        return Asteroid(size, direction, lin_speed, rot_speed, pos=pos)

    def update(self, dt):
        """Updates the asteroids on the screen and generates new
        asteroids.

        Parameters:
            dt: the time since the last update
        """
        for ast in self.asteroids:
            ast.update(dt)

        # Generate a new asteroid, if the time since last generation
        # exceeds the time until the next generation, and if we're
        # below the maximum number of generated asteroids
        if self.last_gen_time >= self.next_gen_time and \
                self.asteroid_count < self.game_rules.max_total:
            self.asteroids.append(self.__gen_asteroid())
            self.asteroid_count += 1

            # Generate a new time for generation and reset the last
            # generation time
            self.next_gen_time = rand.randint(self.game_rules.min_time,
                                              self.game_rules.max_time)
            self.last_gen_time = 0

        self.last_gen_time += dt

    def draw_asteroids(self):
        """Draws the asteroids on the screen"""
        for ast in self.asteroids:
            ast.draw()


class GameRules(object):
    """Represents a set of rules defining the likelihood of asteroids
    of certain sizes spawning, how often an asteroid will spawn, and
    the maximum number of generated asteroids that can be on the screen
    at one time.

    Attributes:
        small_weight: likelihood of a small asteroid spawning
        medium_weight: likelihood of a medium asteroid spawning
        large_weight: likelihood of a large asteroid spawning
        huge_weight: likelihood of a huge asteroid spawning
        max_total: the maximum number of generated asteroids that can
            be on the screen at one time
        min_time: the minimum time it takes an asteroid to spawn
        max_time: the maximum time it takes an asteroid to spawn

    Notes:
        the weights are not based on percentages, but instead depend on
        how large they are compared to each other. So, if small_weight
        is 6 and medium_weight is 3, then a small asteroid has twice
        the chance of spawning than a medium asteroid
    """
    def __init__(self, small_weight, medium_weight, large_weight, huge_weight,
                 max_total, min_time, max_time):
        self.size_weights = ((Asteroid.Size.SMALL, small_weight),
                             (Asteroid.Size.MEDIUM, medium_weight),
                             (Asteroid.Size.LARGE, large_weight),
                             (Asteroid.Size.HUGE, huge_weight))
        self.max_total = max_total
        self.min_time = min_time
        self.max_time = max_time
