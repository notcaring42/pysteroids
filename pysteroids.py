"""Entry point for running the game"""
# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet
from lib.geometry.vector import Vector
from lib.entities import Ship, Asteroid
from pyglet.window import key
from lib.utils import window_width, window_height

window = pyglet.window.Window(caption='Pysteroids', width=window_width,
                              height=window_height)
# Get the keystate and create the ship
keys = key.KeyStateHandler()
window.push_handlers(keys)
ship = Ship(pos=Vector(100, 100))

# Create an asteroid
asteroid = Asteroid(Asteroid.Size.SMALL, pos=Vector(300, 300), shape_index=0)
asteroid.direction = Vector(1, 1)
asteroid.lin_speed = 1
asteroids = [asteroid]


# Update the components of the game and schedule
# the function to run each frame
def update(dt):
    ship.update(keys, dt)
    asteroid.update(dt)

    # Detects a collision
    if (ship.collides(asteroid)):
        # Set the new asteroid array
        global asteroids
        asteroids = [ast for ast in asteroid.destroy()]

pyglet.clock.schedule(update)


# Draw the components to the screen
@window.event
def on_draw():
    window.clear()
    ship.draw()
    for ast in asteroids:
        ast.draw()

pyglet.app.run()
