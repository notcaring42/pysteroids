"""Holds classes related to visual and audio effects"""
import random as rand

from lib.entities import Entity
from lib.utils import rand_direction, WINDOW_WIDTH, WINDOW_HEIGHT, Singleton
from lib.geometry.vector import Vector

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


class Animation(object):
    """An animation which can be drawn to the screen

    Attributes:
        name: the name of the animation
        particles: a list of Entities which act as the particles in
                   the animation
        lifespan: the amount of time the animation plays for,
                  in seconds
        current_life: the amount of time the animation has played for
                      so far, in seconds
        is_active: is the animation currently active?
    """
    def __init__(self, name, particles, lifespan):
        """Creates a new Animation"""
        self.name = name
        self.particles = particles
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

    def draw(self):
        """Draws the animation to the screen"""
        for particle in self.particles:
            particle.draw()

class RandomAnimation(Animation):
    """An animation in which the particles are randomized in some way

    Attributes:
        particle_gen: the function used to generate a new set of random
                      particles
    """
    def __init__(self, name, lifespan, particle_gen):
        """Creates a new RandomAnimation"""
        self.name = name
        self.lifespan = lifespan
        self.particle_gen = particle_gen
        self.current_life = 0
        self.is_active = False

        # Generate an initial set of random particles
        self.particles = particle_gen()

    def update(self, dt):
        """Updates the RandomAnimation's particles

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

            # Generate a new set of random particles
            self.particles = self.particle_gen()

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
                              rand_direction(Vector(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)),
                              lin_speed)
            fragments.append(fragment)
        return fragments
    animations['PLAYER_DEAD'] = RandomAnimation('PLAYER_DEAD', 2, pd_gen_particles)

    return animations
