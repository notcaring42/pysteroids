"""Entry point for running the game"""
# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet
from pyglet.window import key
from pyglet.gl import glLoadIdentity

from lib.geometry.vector import Vector
from lib.entities import Ship, Asteroid
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
        asteroid = Asteroid(Asteroid.Size.HUGE, Vector(1, 1), 1, 1,
                            pos=Vector(300, 300), shape_index=0)
        asteroid.direction = Vector(1, 1)
        asteroid.lin_speed = 0
        self.asteroids = [asteroid]
        self.player_dead = False
        self.game_over = False
        self.lives_left = 3
        self.lives_left_label = \
            pyglet.text.Label('Lives Left: ' + str(self.lives_left),
                              font_name='Droid Sans Mono',
                              font_size=12,
                              x=70, y=WINDOW_HEIGHT-15,
                              anchor_x='center', anchor_y='center')
        # Register and schedule the update function
        pyglet.clock.schedule(self.update)

    def update(self, dt):
        """
        Updates the game entities

        Args:
            dt: time since the last update
        """
        # Update the entities
        for ast in self.asteroids:
            ast.update(dt)

        if self.player_dead:
            return

        self.ship.update(self.keys, dt)
        # Check for bullet hits
        for asteroid in self.asteroids:
            if asteroid.collides(self.ship):
                self.player_dead = True
                self.lives_left -= 1
                if self.lives_left == 0:
                    self.game_over = True
                    break
                self.lives_left_label.text = ('Lives Left: ' +
                                              str(self.lives_left))
                del self.ship
                pyglet.clock.schedule_once(self.respawn_player, 3)
                break
            for bullet in self.ship.bullets:
                if bullet.collides(asteroid):
                    self.asteroids.remove(asteroid)
                    self.asteroids.extend(asteroid.destroy())
                    self.ship.bullets.remove(bullet)

    def on_draw(self):
        """
        Handler for the on_draw event of the game window
        """
        self.window.clear()

        glLoadIdentity()

        if self.game_over:
            self.draw_game_over()
        else:
            self.lives_left_label.draw()
            if not self.player_dead:
                self.ship.draw()

        for ast in self.asteroids:
            ast.draw()

    def respawn_player(self, dt):
        self.ship = Ship(pos=Vector(100, 100))
        self.player_dead = False

    def draw_game_over(self):
        game_over_label = pyglet.text.Label('GAME OVER!',
                                            font_name='Droid Sans Mono',
                                            font_size=32,
                                            x=WINDOW_WIDTH//2,
                                            y=WINDOW_HEIGHT//2,
                                            anchor_x='center',
                                            anchor_y='center')
        game_over_label.draw()

# Initialize the game and start it
if __name__ == '__main__':
    Pysteroids()
    pyglet.app.run()
