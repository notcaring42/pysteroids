import random as rand

from lib.entities import Entity
from lib.utils import rand_direction, WINDOW_WIDTH, WINDOW_HEIGHT
from lib.geometry.vector import Vector


class EffectPlayer(object):
    def __init__(self):
        self.active_animations = []
        self.animations = generate_animations()

    def update(self, dt):
        for animation in self.active_animations:
            animation.update(dt)
            if not animation.is_active:
                self.active_animations.remove(animation)

    def draw_animations(self):
        for animation in self.active_animations:
            animation.draw()

    def play_animation(self, name, pos):
        animation = self.animations[name]
        animation.play(pos)
        self.active_animations.append(animation)


class Animation(object):
    def __init__(self, name, particles, lifespan):
        self.name = name
        self.particles = particles
        self.lifespan = lifespan
        self.current_life = 0
        self.is_active = False

    def play(self, pos):
        self.is_active = True
        for particle in self.particles:
            particle.pos = pos

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
        self.current_life += dt
        if self.current_life >= self.lifespan:
            self.current_life = 0
            self.is_active = False


    def draw(self):
        for particle in self.particles:
            particle.draw()

class RandomAnimation(Animation):
    def __init__(self, name, lifespan, particle_gen):
        self.name = name
        self.lifespan = lifespan
        self.particle_gen = particle_gen
        self.particles = particle_gen()
        self.current_life = 0
        self.is_active = False

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
        self.current_life += dt
        if self.current_life >= self.lifespan:
            self.current_life = 0
            self.is_active = False
            self.particles = self.particle_gen()

def generate_animations():
    animations = {}

    # PLAYER_DEAD
    # Random Animation
    # Generate a bunch of little squares
    def pd_gen_particles():
        fragments = []
        for i in range(1, 41):
            lin_speed = rand.uniform(0.5, 1.5)
            fragment = Entity((-1, 1, 1, 1, 1, -1, -1, -1),
                              rand_direction(Vector(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)),
                              lin_speed)
            fragments.append(fragment)
        return fragments
    animations['PLAYER_DEAD'] = RandomAnimation('PLAYER_DEAD', 2, pd_gen_particles)

    return animations
