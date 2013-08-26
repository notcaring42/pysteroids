"""Contains classes for managing game rules"""
import sys
import random as rand

import pyglet

from entities import Asteroid
from geometry.vector import Vector
from utils import weighted_choice, WINDOW_WIDTH, \
    WINDOW_HEIGHT, rand_direction


class AsteroidManager(object):
    """Uses game rules to generate asteroids

    Attributes:
        asteroids: list of currently active asteroids
        asteroid_count: the number of GENERATED asteroids in play
        curr_level: the currently active game rules used to generate
            asteroids
        all_levels: the master list of all game rules
        curr_level_num: the current level the player is on
        next_gen_time: the time until the next asteroid will be
            generated
        last_gen_time: the time since the last asteroid was generated
        on_level_change: callback function to invoke when the player
            completes a level
    """
    def __init__(self, on_level_change):
        """Creates a new AsteroidManager

        Parameters:
            on_level_change: function to call when the player moves to
                the next level. Requires a parameter for the class to
                pass back the new level number

        Returns:
            a new AsteroidManager
        """
        self.asteroids = []
        self.asteroid_count = 0
        self.all_levels = self._parse_levels()
        self.curr_level = self.all_levels.pop()
        self.curr_level_num = 1
        self.on_level_change = on_level_change
        self.next_gen_time = 0
        self.last_gen_time = 0

    def _parse_levels(self):
        """Parses the game levels from levels.txt

        Returns:
            a list of Levels
        """
        all_levels = []

        try:
            rules_file = pyglet.resource.file('levels.txt', 'r')
        except IOError:
            # The levels file doesn't exist!
            sys.exit('ERROR: Levels file (res/levels.txt) not found!')

        for line in rules_file:
            # Make an array out of the line entries
            entries = line.split(' ')

            try:
                # Transform each entry into an int, and create a Level
                # using them
                entries = [int(i) for i in entries]
                parsed_rules = Level(entries[0], entries[1], entries[2],
                                     entries[3], entries[4], entries[5],
                                     entries[6])
            except IndexError, ValueError:
                # There weren't enough entries, or the entries are not
                # numbers
                sys.exit("""ERROR: levels.txt corrupt! Are all the entries
                    numbers, and are there a correct amount (7) per line?""")

            all_levels.append(parsed_rules)

        # We're going to pop each Level off one by one, so we need to
        # reverse the list so that earlier levels are at the end of the
        # list
        all_levels.reverse()

        return all_levels

    def _gen_asteroid(self):
        """Generates a new asteroid

        Returns:
            a new, randomly generated asteroid
        """
        # Get a random size, with probability depending on the game
        # rules
        size = weighted_choice(self.curr_level.size_weights)

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
                self.asteroid_count < self.curr_level.max_total:
            self.asteroids.append(self._gen_asteroid())
            self.asteroid_count += 1

            # Generate a new time for generation and reset the last
            # generation time
            self.next_gen_time = rand.randint(self.curr_level.min_time,
                                              self.curr_level.max_time)
            self.last_gen_time = 0

        # If there are no asteroids left in play, go to the next level
        if len(self.asteroids) == 0:
            # Reset regen values so we generate a new asteroid
            # immediately, and reset the count
            self.last_gen_time = 0
            self.next_gen_time = 0
            self.asteroid_count = 0

            # If we're not out of levels, move to the next one
            # Otherwise, we just restart on the last level
            if len(self.all_levels) != 0:
                self.curr_level = self.all_levels.pop()
                self.curr_level_num += 1

            # Invoke the callback
            self.on_level_change(self.curr_level_num)

            return

        self.last_gen_time += dt

    def draw_asteroids(self):
        """Draws the asteroids on the screen"""
        for ast in self.asteroids:
            ast.draw()


class Level(object):
    """Represents a set of rules defining the likelihood of asteroids
    of certain sizes spawning, how often an asteroid will spawn, and
    the maximum number of asteroids generated for this level.

    Attributes:
        small_weight: likelihood of a small asteroid spawning
        medium_weight: likelihood of a medium asteroid spawning
        large_weight: likelihood of a large asteroid spawning
        huge_weight: likelihood of a huge asteroid spawning
        max_total: the maximum number of asteroids that can be generated
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
