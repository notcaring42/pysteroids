Pysteroids
==========

**Pysteroids** is an Asteroids clone written in Python and using the
[Pyglet](http://www.pyglet.org "Pyglet") multimedia library.
All of the graphics are done via OpenGL calls exposed by Pyglet,
no images are used. I wanted to capture the 'retro' feel of playing
Asteroids on Atari or Intellivision or whatever, as well as practice
applying some mathematics to programming (mostly in the form of linear
algebra and the separating axis theorem). All of the sounds were created
using [sfxr](http://www.drpetter.se/project_sfxr.html "sfxr").

Essentially all of the code is written by me, but I might've adapted some sample code
for collision and such, because math is really hard.

Installing
----------
Pysteroids is available from [PyPI](https://pypi.python.org/pypi/pysteroids "PyPI"),
and can be installed using pip by running

    pip install pysteroids

Setuptools should automatically pull down any dependencies. You also need to have either 
[OpenAL](https://en.wikipedia.org/wiki/OpenAL "OpenAL") or
[AVBin](http://avbin.github.io/AVbin/Home/Home.html "AVBin") installed for audio to work.

Pip should put an entry point called 'pysteroids' in /usr/bin on Mac and Linux and
the Python 'Scripts' folder on Windows, which you can then run to start the game.

Controls
--------
-  W: move forward
-  A/D: rotate
-  Space: shoot
-  Shift: teleport

Dependencies
------------
Pysteroids uses Python 2.7 and depends on the following Python libraries:

-  **Numpy** (>= 1.7.1)
-  **Pyglet** (> 1.4.1, specifically 1.2alpha1)

Again, Setuptools should pull these down automatically when you install Pysteroids.

Pysteroids uses a 
[Pyglet alpha version](http://code.google.com/p/pyglet/downloads/list?q=1.2alpha1 "Pyglet 1.2alpha") 
instead of the version on PyPI (1.1.4) because of an issue with Pyglet 1.1.4 not initializing correctly on some systems, described
[here](https://code.google.com/p/pyglet/issues/detail?id=456 "Pyglet issue"). The patch
for this issue is in the current development version (1.2alpha1), but has not been backported
to 1.1.4. Development of Pyglet seems to be at a standstill at the moment, so this is the best
solution I could come up with.

If you don't want to update, you can get the source from 
[PyPI](https://pypi.python.org/pypi/pysteroids "PyPI") and modify setup.py by changing

    install_requires = ['numpy>=1.7.1',
                        'pyglet>1.1.4']

to

    install_requires = ['numpy>=1.7.1',
                        'pyglet==1.1.4']

and removing the line

    dependency_links = ['http://pyglet.googlecode.com/files/' +
                        'pyglet-1.2alpha1.tar.gz#egg=pyglet-1.2alpha1'],

Then get the dependencies from pip:

    pip install numpy pyglet

And finally, install with

    python setup.py install

Be warned that you may get the same error described above if you try this.
