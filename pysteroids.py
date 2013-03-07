# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet
from lib.entities import Entity
from lib.utils import Shape, Vector
from math import asin, degrees

window = pyglet.window.Window(caption='Pysteroids')

# Creates a test ship to demonstrate Entity and Shape classes
# We set the rotation such that the ship will travel across
# the diagnol of the window
s = Shape((30, 0, -30, 20, -30, -20))
e = Entity(s)
windowSlope = Vector(window.width, window.height)
windowSlope.normalize()
e.rot = degrees(asin(windowSlope.y))


@window.event
def on_draw():
    window.clear()
    e.pos += e.direction * 2
    e.draw()

pyglet.app.run()
