# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet
from lib.entities import Ship
from lib.utils import Vector, Shape
from pyglet.window import key

window = pyglet.window.Window(caption='Pysteroids')

# Get the keystate and create the ship
keys = key.KeyStateHandler()
window.push_handlers(keys)
ship = Ship(keys, pos=Vector(100, 100))

# Create a testShape to test collision
testShape = Shape((100, 0, 0, -100, 0, 100),
                  pos=Vector(300, 300), rot=0.0, scale=1.0)


# Update the components of the game and schedule
# the function to run each frame
def update(dt):
    ship.update(dt)
    print ship.collides(testShape)

pyglet.clock.schedule(update)


@window.event
def on_draw():
    window.clear()
    ship.draw()
    testShape.draw()

pyglet.app.run()
