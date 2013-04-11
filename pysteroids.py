"""Entry point for running the game"""
# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet
from lib.geometry.vector import Vector
from lib.entities import Ship, Asteroid
from pyglet.window import key
from lib.utils import WINDOW_WIDTH, WINDOW_HEIGHT


class Pysteroids(object):
    """
    Runs the game and manages game variables

    Attributes:
        window: the game window
        keys: the key state
        ship: the player's ship
        asteroids: a list of the currently active asteroids
    """
    def __init__(self):
        """
        Starts the game
        """
        # Create the window and register the draw handler
        self.window = pyglet.window.Window(caption='Pysteroids',
                                           width=WINDOW_WIDTH,
                                           height=WINDOW_HEIGHT)
        self.window.on_draw = self.on_draw

        # Add key handler to keep track of key presses
        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)

        # Create game entities
        self.ship = Ship(pos=Vector(100, 100))
        asteroid = Asteroid(Asteroid.Size.SMALL, Vector(1, 1), 1, 1,
                            pos=Vector(300, 300), shape_index=0)
        asteroid.direction = Vector(1, 1)
        asteroid.lin_speed = 1
        self.asteroids = [asteroid]

        # Register and schedule the update function
        pyglet.clock.schedule(self.update)

    def update(self, dt):
        """
        Updates the game entities

        Args:
            dt: time since the last update
        """
        # Update the entities
        self.ship.update(self.keys, dt)
        for ast in self.asteroids:
            ast.update(dt)

        # Check for collision
        for asteroid in self.asteroids:
            if self.ship.collides(asteroid):
                # Remove the destroyed asteroid, and add
                # any new asteroids resulting from the old one
                self.asteroids.remove(asteroid)
                self.asteroids.extend(asteroid.destroy())

    def on_draw(self):
        """
        Handler for the on_draw event of the game window
        """
        self.window.clear()
        self.ship.draw()
        for ast in self.asteroids:
            ast.draw()

# Initialize the game and start it
Pysteroids()
pyglet.app.run()
