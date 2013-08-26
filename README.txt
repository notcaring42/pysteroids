PYSTEROIDS
==========

Pysteroids is a clone of the game Asteroids written in Python. Although
I call it a clone, I might have added a few bells and whistles that weren't
in the original (I'm not exactly sure what the original had).

Also, this is the first game I've finished to completion, so it may not
be the best. I did work hard on it, so hopefully you'll have fun with it!
If not, oh well.

Dependencies
------------
Pysteroids depends on the following libraries:
NumPy >= 1.7.1
Pyglet > 1.4.1 (specifically, 1.2alpha1)

When installing, setuptools should pull these down automatically. It will
pull Pyglet from it's development site at 
http://code.google.com/p/pyglet/downloads/list?q=1.2alpha1, if you don't have it.
The PyPI version of Pyglet (1.4.1) doesn't include a patch which fixes some issues described here:
https://code.google.com/p/pyglet/issues/detail?id=456
Not all users may have this issue, but Pyglet 1.2alpha1 seems to be stable and SHOULD
work for everyone. If not, you can change the dependency in setup.py and try the stable version.
Unfortunately, Pyglet development seems to be at a standstill, so this is the best option
I could come up with.

Controls
--------
W: Move ship forward
A/D: Rotate ship
Space: Fire
Shift: Teleport

License
-------
Pysteroids is copyrighted under the MIT license. A copy of it should be included in the source
distribution, in a file called LICENSE.txt. You can get more info there. The source code at
Github also has the license.

Source
------
You can find the source code in full at https://github.com/Cheeser12/pysteroids