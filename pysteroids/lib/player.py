"""Contains the Ship entity class which represents the player on the
screen, and the Player class which holds player variables and wraps
the Ship class
"""
from math import sin, cos, radians
from random import randint

from pyglet.clock import schedule_once
from pyglet.window import key

from utils import Vector, clamp, WINDOW_WIDTH, WINDOW_HEIGHT
from entities import Entity, Bullet
from effect import EffectPlayer


class Player(object):
    """Holds player variables and wraps around the Ship class

    Attributes:
        ship: the player's Ship
        is_vulnerable: is the player vulnerable to being destroyed?
        is_dead: is the player dead?
        teleport_up: is the player's teleport ability active?
        lives_left: number of lives the player has left
        game_over: is the player out of lives?
        score: the player's score
        bullets: the player's active Bullets
        effect_player: the game's EffectPlayer
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
        self.effect_player = EffectPlayer.instance()

    @property
    def teleport_up(self):
        return self.ship.teleport_up

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

        # Play death animation
        self.effect_player.play_animation('PLAYER_DEAD', self.ship.pos)

        # Subtract a life and check if the player still has any
        # lives left
        self.lives_left -= 1
        if self.lives_left == 0:
            self.game_over = True
            return

        # Schedule the player for respawn in 3 seconds
        schedule_once(self._respawn, 3)

    def _respawn(self, dt):
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
        schedule_once(self._set_vulnerable, 2)

    def _set_vulnerable(self, dt):
        """Makes the player vulnerable to destruction again

        Parameters:
            dt: not applicable, required for a clock callback function
        """
        self.is_vulnerable = True


class Ship(Entity):
    """Defines the player's ship.

    An extension of the entity class, but with a self-defined shape and
    input handling.

    Attributes:
        _max_speed: the maximum units per update that the ship can
                     travel
        _movement: the movement vector that the ship is translated by
                    each frame
        _shoot_delay: time that must elapse before the player can
                       shoot again
        _teleport_delay: time that must elapse before the player can
                          teleport again
        _last_shoot: amount of time since the player last shot
        _last_teleport: amount of time since the player last
                         teleported
        teleport_up: is the ship's teleport available?
        bullets: a list of bullets shot by the player that are in play
        effect_player: the game's EffectPlayer
    """

    _max_speed = 1.5
    _shoot_delay = 0.8
    _teleport_delay = 14.0

    def __init__(self, pos=Vector(0, 0), rot=0.0):
        """Creates a new Ship

        Args:
            pos: the position of the ship
            rot: the rotation of the ship

        Returns:
            a new Ship instance
        """

        # Get the initial direction of the ship using the rotation
        direction = Vector(cos(radians(rot)), sin(radians(rot)))

        # Initially, the ship isn't moving
        self._movement = Vector.zero()

        # Initialize bullet list
        self.bullets = []
        self._last_shoot = self._shoot_delay
        self._last_teleport = self._teleport_delay
        self.teleport_up = True
        self.effect_player = EffectPlayer.instance()
        Entity.__init__(self, (20, 0, -30, 20, -30, -20), direction,
                        lin_speed=1.0, rot_speed=2.0, pos=pos, rot=rot,
                        scale=0.5)

    def _handle_input(self, keys, dt):
        """Handles any input from the player.

        Args:
            keys: the keyboard state
            dt: the amount of time since the last update
        """

        # Moves the ship forward
        #
        # Moving works like this: each frame the ship is translated
        # by the movement vector. When the ship moves forward, a scalar
        # multiple of the direction vector is added to the movement
        # vector. This simulates zero-gravity movement for the ship:
        # even if the player is facing a different direction, the
        # movement still continues in the same direction until
        # thrusters are engaged
        if keys[key.W]:
            self._movement += self._direction * self.lin_speed * dt

        # Set a maximum speed
        # Normalize the movement vector and then multiply
        # by the new length to get the new speed
        new_length = clamp(self._movement.length(),
                           -self._max_speed, self._max_speed)
        self._movement = self._movement.normalize()
        self._movement *= new_length

        # Rotate the ship
        if keys[key.A]:
            self.rot += self.rot_speed
        elif keys[key.D]:
            self.rot -= self.rot_speed

        # Shoot a bullet, but check to make sure that the time
        # since the last shot is greater than the delay
        if keys[key.SPACE] and (self._last_shoot >= self._shoot_delay):
            bullet_pos = self.pos + 3*self.direction
            self.bullets.append(Bullet(bullet_pos, self.rot,
                                       self.direction))
            self._last_shoot = 0
            self.effect_player.play_sound('SHOOT')
        else:
            self._last_shoot += dt

        # Is the ship's teleport available?
        if self._last_teleport >= self._teleport_delay:
            self.teleport_up = True

        # Teleport the ship to a random location
        if keys[key.LSHIFT] and self.teleport_up:
            # Put the player way off the screen to make it look
            # like he's teleporting, and to avoid possible collisions
            self.effect_player.play_animation('PLAYER_TELEPORT', self.pos)
            self.effect_player.play_sound('TELEPORT')
            self.pos = Vector(5000, 5000)
            schedule_once(self._teleport, 1.5)
            self._last_teleport = 0
            self.teleport_up = False
        else:
            self._last_teleport += dt

    def update(self, keys, dt):
        """Updates the ship and handles input

        Args:
            keys: the keyboard state
            dt: the amount of time since the last update
        """
        # Move the ship
        self._handle_input(keys, dt)
        self.pos += self._movement

        # Update variables
        self._shape.pos = self.pos
        self._shape.rot = self.rot
        self._shape.scale = self.scale

        # Reflect across the screen, if necessary
        self._reflect_across_screen()

        # Update each bullet, and remove if necessary
        for bullet in self.bullets:
            bullet.update(dt)

            if bullet.expired is True:
                self.bullets.remove(bullet)

    def draw(self):
        Entity.draw(self)
        for bullet in self.bullets:
            bullet.draw()

    def _teleport(self, dt):
        # We give a buffer of 20 units so the ship doesn't teleport
        # to the very edge of the screen
        self.pos = Vector(randint(20, WINDOW_WIDTH-20),
                          randint(20, WINDOW_HEIGHT-20))

    # Direction stored as a property to ensure normalization
    @property
    def direction(self):
        return self._direction

    # Setting the rotation of the ship also sets the new direction
    @property
    def rot(self):
        return self._rot

    @rot.setter
    def rot(self, value):
        self._rot = value

        # Set new direction vector
        self._direction = Vector(cos(radians(value)), sin(radians(value)))
