"""Entry point for running the game"""
# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet
from pyglet.window import key
from pyglet.gl import glLoadIdentity

from lib.geometry.vector import Vector
from lib.entities import Ship, Asteroid
from lib.utils import WINDOW_WIDTH, WINDOW_HEIGHT
from lib.game_rules import AsteroidManager


class Pysteroids(object):
    """Runs the game and manages game variables

    Attributes:
        window: the game window
        keys: the key state
        ship: the player's ship
        asteroids: a list of the currently active asteroids
        fps_display: a display to show the current FPS of the
            application
        game_rules: the current set of game rules, defining how
            many asteroids can be on the screen per type
        asteroid_manager: the AsteroidManager responsible for
            generating new asteroids based on the game rules
        player_dead: a boolean value representing whether or not
            the player is dead right now
        player_vulnerable: a boolean value representing whether or not
            the player is vulnerable to being destroyed by an asteroid
        game_over: a boolean value representing whether or not the player
            has run out of lives
        lives_left: the number of lives the player has Left
        score: the player's current score
        lives_left_label: a label for displaying the number of lives
            the player has left
        score_label: a label for displaying the player's score
        level_label: a label for displaying the current level the
            player is on
    """
    def __init__(self):
        """Starts the game"""
        # Create the window and register the draw handler
        self.window = pyglet.window.Window(caption='Pysteroids',
                                           width=WINDOW_WIDTH,
                                           height=WINDOW_HEIGHT)
        self.window.on_draw = self.on_draw

        # Create a display to show FPS
        self.fps_display = pyglet.clock.ClockDisplay()

        # Add key handler to keep track of key presses
        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)

        # Create game entities
        self.ship = Ship(pos=Vector(100, 100))

        # Create game rules and an asteroid manager to generate
        # asteroids
        self.asteroid_manager = AsteroidManager(self.on_level_change)

        # Set player variables
        self.player_dead = False
        self.player_vulnerable = True
        self.game_over = False
        self.lives_left = 3
        self.score = 0

        # Create a label for displaying the number of lives left
        self.lives_left_label = \
            pyglet.text.Label('Lives Left: ' + str(self.lives_left),
                              font_name='Droid Sans Mono',
                              font_size=12,
                              x=70, y=WINDOW_HEIGHT-15,
                              anchor_x='center', anchor_y='center')

        # Create a score label
        self.score_label = \
            pyglet.text.Label('Score: ' + str(self.score),
                              font_name='Droid Sans Mono',
                              font_size=12,
                              x=WINDOW_WIDTH-70, y=WINDOW_HEIGHT-15,
                              anchor_x='center', anchor_y='center')

        # Create a lable for displaying the current level
        self.level_label = \
            pyglet.text.Label('Level: ' + str(self.asteroid_manager.curr_level_num),
                              font_name='Droid Sans Mono',
                              font_size=12,
                              x=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT-15,
                              anchor_x='center', anchor_y='center')

        # Register and schedule the update function
        pyglet.clock.schedule(self.update)

    def update(self, dt):
        """Updates the game entities

        Args:
            dt: time since the last update
        """
        # Update the asteroids
        self.asteroid_manager.update(dt)

        # If the player is dead, we don't have to update
        # the ship or check for collisions
        if self.player_dead:
            return
        self.ship.update(self.keys, dt)

        # Check for bullet hits
        for asteroid in self.asteroid_manager.asteroids:
            # We only need to check collisions if the player is
            # vulnerable, so if the player is not this will
            # short-circuit
            if self.player_vulnerable and asteroid.collides(self.ship):
                # Mark the player has dead and subtract a life
                self.player_dead = True
                self.lives_left -= 1

                # If the player is out of lives, game over!
                if self.lives_left == 0:
                    self.game_over = True
                    break
                # Update the display to reflect the new number of lives
                self.lives_left_label.text = ('Lives Left: ' +
                                              str(self.lives_left))

                # Clear out the ship variable, and set a respawn
                # for 3 seconds.
                del self.ship
                pyglet.clock.schedule_once(self.respawn_player, 3)
                break
            # Check bullet collisions
            for bullet in self.ship.bullets:
                if bullet.collides(asteroid):
                    # Remove the current asteroid and add the asteroids
                    # that result from the destruction, if there are any
                    self.asteroid_manager.asteroids.remove(asteroid)
                    self.asteroid_manager.asteroids.extend(asteroid.destroy())

                    # For scoring, we only add to the player's score if
                    # the asteroid that was destroyed was small. This
                    # is easier than assigning a point value to each
                    # size of asteroid, because bigger asteroids will
                    # automatically be worth more since they 'contain'
                    # many small asteroids
                    if asteroid.size == Asteroid.Size.SMALL:
                        self.score += 10
                        self.score_label.text = 'Score: ' + str(self.score)

                    # Remove the bullet from the screen
                    self.ship.bullets.remove(bullet)

    def on_draw(self):
        """Handler for the on_draw event of the game window"""
        self.window.clear()

        # Reset to the identity view matrix
        glLoadIdentity()

        # Draw FPS
        self.fps_display.draw()

        # Draw the game over screen if the player is out of lives,
        # otherwise draw the lives left and the player (if not dead)
        if self.game_over:
            self.draw_game_over()
        else:
            self.lives_left_label.draw()
            self.score_label.draw()
            self.level_label.draw()
            if not self.player_dead:
                self.ship.draw()

        # Always draw the asteroids
        self.asteroid_manager.draw_asteroids()

    def respawn_player(self, dt):
        """Respawns the player's ship.

        Parameters:
            dt: not applicable, included because scheduling with pyglet
                requires it as a parameter
        """
        # Create a new ship and reset player variables
        self.ship = Ship(pos=Vector(100, 100))
        self.player_dead = False
        self.player_vulnerable = False

        # Initially, the player is not vulnerable to destruction.
        # Schedule vulnerability for 3 seconds after spawn.
        pyglet.clock.schedule_once(self.set_vulnerable, 3)

    def on_level_change(self, level_num):
        """Callback for AsteroidManager, invoked when the player
        completes a level

        Parameters:
            level_num: the new level number the player is on
        """
        self.level_label.text = ('Level: ' + str(self.asteroid_manager
                                                     .curr_level_num))

        # Give the player some bonus points for completing a level
        self.score += 50

    def draw_game_over(self):
        """Draws the game over screen"""
        # Create a game over label and draw it
        game_over_label = pyglet.text.Label('GAME OVER!',
                                            font_name='Droid Sans Mono',
                                            font_size=32,
                                            x=WINDOW_WIDTH//2,
                                            y=WINDOW_HEIGHT//2,
                                            anchor_x='center',
                                            anchor_y='center')
        game_over_label.draw()

    def set_vulnerable(self, dt):
        """Sets the player as vulnerable to destruction

        Parameters:
            dt: not applicable, included because scheduling with pyglet
                requires it as a parameter
        """
        self.player_vulnerable = True

# Initialize the game and start it
if __name__ == '__main__':
    Pysteroids()
    pyglet.app.run()
