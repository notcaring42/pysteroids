"""Holds classes related to visual and audio effects"""
import random as rand

import pyglet

from entities import Entity
from utils import rand_direction, WINDOW_WIDTH, WINDOW_HEIGHT, Singleton
from geometry.vector import Vector


# EffectPlayer will be a singleton, since only one instance is needed,
# and to allow easy access to the instance through the class
@Singleton
class EffectPlayer(object):
    """Plays visual and audio effects throughout the game.

    This is a singleton, and should be accessed through
    'EffectPlayer.instance()'.

    Attributes:
        animations: a dictionary of animations that can be played
        active_animations: a list of animations currently being played
    """
    def __init__(self):
        """Creates a new EffectPlayer"""
        self.active_animations = []
        self.animations = generate_animations()
        self.sounds = generate_sounds()

    def update(self, dt):
        """Updates all active effects

        Parameters:
            dt: the time since the last update
        """
        # Update currently playing animations
        for animation in self.active_animations:
            animation.update(dt)

            # If the animation is expired, remove it
            if not animation.is_active:
                self.active_animations.remove(animation)

    def draw_animations(self):
        """Draw all animations currently playing"""
        for animation in self.active_animations:
            animation.draw()

    def play_animation(self, name, pos):
        """Sets an animation as active and to be played

        Parameters:
            name: the name of the animation to be played
            pos: the position the animation should be played at
        """
        animation = self.animations[name]
        animation.play(pos)
        self.active_animations.append(animation)

    def play_sound(self, name):
        """Plays a sound

        Parameters:
            name: the name of the sound to play
        """
        self.sounds[name].play()


class Animation(object):
    """An animation which can be drawn to the screen

    Attributes:
        name: the name of the animation
        particle_gen: the function used to generate particles for the
                      animation
        lifespan: the amount of time the animation plays for,
                  in seconds
        current_life: the amount of time the animation has played for
                      so far, in seconds
        is_active: is the animation currently active?
    """
    def __init__(self, name, lifespan, particle_gen):
        """Creates a new Animation"""
        self.name = name
        self.particles = particle_gen()
        self.particle_gen = particle_gen
        self.lifespan = lifespan
        self.current_life = 0
        self.is_active = False

    def play(self, pos):
        """Marks the animation as active and plays it

        Parameters:
            pos: the position the animation is to be played at
        """
        self.is_active = True

        # Set each particle to the animation position
        for particle in self.particles:
            particle.pos = pos

    def update(self, dt):
        """Updates the animation and its particles

        Parameters:
            dt: the time since the last update
        """
        for particle in self.particles:
            particle.update(dt)
        self.current_life += dt

        # Check if the animation has expired
        if self.current_life >= self.lifespan:
            self.current_life = 0
            self.is_active = False

            # Generate a new set of particles
            self.particles = self.particle_gen()

    def draw(self):
        """Draws the animation to the screen"""
        for particle in self.particles:
            particle.draw()


def generate_animations():
    """Generates a dictionary containing all of the game's animations"""
    animations = {}

    # PLAYER_DEAD
    # Random Animation
    # Generate a bunch of little squares
    def pd_gen_particles():
        fragments = []
        for i in range(1, 41):
            lin_speed = rand.uniform(0.5, 1.5)

            # Note that we generate random directions relative to the
            # middle of the screen, because rand_direction is based on
            # having a reference position in game bounds
            fragment = Entity((-1, 1, 1, 1, 1, -1, -1, -1),
                              rand_direction(Vector(WINDOW_WIDTH//2,
                                                    WINDOW_HEIGHT//2)),
                              lin_speed)
            fragments.append(fragment)
        return fragments
    animations['PLAYER_DEAD'] = Animation('PLAYER_DEAD', 2, pd_gen_particles)

    # PLAYER_TELEPORT
    def pt_gen_particles():
        tele_lines = []

        # Four lines at 45-degree angles to the x-y axes
        tele_rot = [45, 135, 225, 315]
        tele_directions = [Vector(1, 1), Vector(-1, 1), Vector(-1, -1),
                           Vector(1, -1)]
        for rot, direction in zip(tele_rot, tele_directions):
            tele_lines.append(Entity((-3, 0.5, 3, 0.5, 3, -0.5, -3, -0.5),
                              direction, 0.6, rot=rot))
        return tele_lines

    animations['PLAYER_TELEPORT'] = Animation('PLAYER_TELEPORT', 0.8,
                                              pt_gen_particles)

    # ASTEROID_DESTROY
    def ad_gen_particles():
        fragments = []
        for i in range(1, 11):
            lin_speed = rand.uniform(0.5, 1.5)

            # Note that we generate random directions relative to the
            # middle of the screen, because rand_direction is based on
            # having a reference position in game bounds
            fragment = Entity((-1, 1, 1, 1, 1, -1, -1, -1),
                              rand_direction(Vector(WINDOW_WIDTH//2,
                                                    WINDOW_HEIGHT//2)),
                              lin_speed)
            fragments.append(fragment)
        return fragments
    animations['ASTEROID_DESTROY'] = Animation('ASTEROID_DESTROY', 0.6,
                                               ad_gen_particles)

    return animations


def generate_sounds():
    """Generates a dictionary of all the game's sounds"""
    sounds = {}

    # EXPLOSION
    sounds['EXPLOSION'] = pyglet.resource.media('explosion.wav',
                                                streaming=False)

    # RESPAWN
    sounds['RESPAWN'] = pyglet.resource.media('respawn.wav',
                                              streaming=False)

    # SHOOT
    sounds['SHOOT'] = pyglet.resource.media('shoot.wav',
                                            streaming=False)

    # TELEPORT
    sounds['TELEPORT'] = pyglet.resource.media('teleport.wav',
                                               streaming=False)

    return sounds
