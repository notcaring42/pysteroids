# Pysteroids - An Asteroids clone in Python
# Max Mays
import pyglet

window = pyglet.window.Window()


@window.event
def on_draw():
    window.clear()

pyglet.app.run()
