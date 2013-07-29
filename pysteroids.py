"""Entry point for running the game"""
# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet
from pyglet.window import key
from pyglet.gl import glLoadIdentity

from lib.entities import Asteroid
from lib.utils import WINDOW_WIDTH, WINDOW_HEIGHT
from lib.game_rules import AsteroidManager
from lib.player import Player


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

        # Create the player
        self.player = Player()

        # Create game rules and an asteroid manager to generate
        # asteroids
        self.asteroid_manager = AsteroidManager(self.on_level_change)

        # Create a label for displaying the number of lives left
        self.lives_left_label = \
            pyglet.text.Label('Lives Left: ' + str(self.player.lives_left),
                              font_name='Droid Sans Mono',
                              font_size=12,
                              x=70, y=WINDOW_HEIGHT-15,
                              anchor_x='center', anchor_y='center')

        # Create a score label
        self.score_label = \
            pyglet.text.Label('Score: ' + str(self.player.score),
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
        if self.player.is_dead:
            return
        self.player.update(self.keys, dt)

        # Check for bullet hits
        for asteroid in self.asteroid_manager.asteroids:
            # We only need to check collisions if the player is
            # vulnerable, so if the player is not this will
            # short-circuit
            if self.player.is_vulnerable and asteroid.collides(self.player
                                                                   .ship):
                self.player.kill()

                # Update the display to reflect the new number of lives
                self.lives_left_label.text = ('Lives Left: ' +
                                              str(self.player.lives_left))
                break

            # Check bullet collisions
            for bullet in self.player.bullets:
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
                        self.player.score += 10
                        self.score_label.text = 'Score: ' + str(self.player
                                                                    .score)

                    # Remove the bullet from the screen
                    self.player.bullets.remove(bullet)

    def on_draw(self):
        """Handler for the on_draw event of the game window"""
        self.window.clear()

        # Reset to the identity view matrix
        glLoadIdentity()

        # Draw FPS
        self.fps_display.draw()

        # Draw the game over screen if the player is out of lives,
        # otherwise draw the lives left and the player (if not dead)
        if self.player.game_over:
            self.draw_game_over()
        else:
            self.lives_left_label.draw()
            self.score_label.draw()
            self.level_label.draw()
            if not self.player.is_dead:
                self.player.draw()

        # Always draw the asteroids
        self.asteroid_manager.draw_asteroids()

    def on_level_change(self, level_num):
        """Callback for AsteroidManager, invoked when the player
        completes a level

        Parameters:
            level_num: the new level number the player is on
        """
        self.level_label.text = ('Level: ' + str(self.asteroid_manager
                                                     .curr_level_num))

        # Give the player some bonus points for completing a level
        self.player.score += 50

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

        # Display the player's final score
        final_score_label = pyglet.text.Label(('Your Score: ' +
                                              str(self.player.score)),
                                              font_name='Droid Sans Mono',
                                              font_size=26,
                                              x=WINDOW_WIDTH//2,
                                              y=WINDOW_HEIGHT//2 - 35,
                                              anchor_x='center',
                                              anchor_y='center')
        game_over_label.draw()
        final_score_label.draw()

# Initialize the game and start it
if __name__ == '__main__':
    Pysteroids()
    pyglet.app.run()
