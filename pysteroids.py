# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet
from lib.entities import Ship
from lib.utils import Vector
from pyglet.window import key

window = pyglet.window.Window(caption='Pysteroids')

# Get the keystate and create the ship
keys = key.KeyStateHandler()
window.push_handlers(keys)
ship = Ship(keys, pos=Vector(100, 100))


# Update the components of the game and schedule
# the function to run each frame
def update(dt):
    ship.update(dt)

pyglet.clock.schedule(update)


@window.event
def on_draw():
    window.clear()
    ship.draw()


pyglet.app.run()
