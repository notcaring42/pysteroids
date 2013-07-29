"""Class which holds player variables and acts as a gateway to the
Ship class"""
from pyglet.clock import schedule_once

from lib.utils import Vector, WINDOW_WIDTH, WINDOW_HEIGHT
from lib.entities import Ship


class Player(object):
    """Holds player variables and wraps around the Ship class

    Attributes:
        ship: the player's Ship
        is_vulnerable: is the player vulnerable to being destroyed?
        is_dead: is the player dead?
        lives_left: number of lives the player has left
        game_over: is the player out of lives?
        score: the player's score
        bullets: the player's active Bullets
    """
    def __init__(self):
        """Initializes player variables and creates his Ship

        Returns:
            a new Player
        """
        # Create the player in the (approximate) middle of the screen
        # and face him upwards
        self.ship = Ship(pos=Vector(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
                         rot=90)
        self.is_vulnerable = True
        self.is_dead = False
        self.lives_left = 3
        self.game_over = False
        self.score = 0
        self.bullets = self.ship.bullets

    def update(self, keys, dt):
        """Updates the player's ship

        Parameters:
            keys: the current keyboard state
            dt: the amount of time since the last update
        """
        self.ship.update(keys, dt)

    def draw(self):
        """Draws the player onto the screen"""
        self.ship.draw()

    def kill(self):
        """Kills the player and schedules him for respawn"""
        self.is_dead = True

        # Subtract a life and check if the player still has any
        # lives left
        self.lives_left -= 1
        if self.lives_left == 0:
            self.game_over = True
            return

        # Schedule the player for respawn in 3 seconds
        schedule_once(self.__respawn, 3)

    def __respawn(self, dt):
        """Respawns the player and his ship

        Parameters:
            dt: not applicable, required for a clock callback function
        """
        # Recreate the ship in the middle of the screen and reset the
        # reference to the player's bullets
        self.ship = Ship(pos=Vector(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
                         rot=90)
        self.bullets = self.ship.bullets
        self.is_dead = False

        # For 2 seconds the player is not vulnerable to destruction in case
        # there is an asteroid in the middle of the screen
        self.is_vulnerable = False
        schedule_once(self.__set_vulnerable, 2)

    def __set_vulnerable(self, dt):
        """Makes the player vulnerable to destruction again

        Parameters:
            dt: not applicable, required for a clock callback function
        """
        self.is_vulnerable = True
