from setuptools import setup, find_packages

setup(
    name = 'pysteroids',
    version = '1.0.1',
    description = ('A clone of the game Asteroids, '
                   'with some extra bells and whistles'),
    author = 'Max Mays',
    author_email = 'wmays@max-mays.com',
    keywords = 'game asteroids',
    license = 'MIT',
    url='https://github.com/Cheeser12/pysteroids',
    entry_points = {
        'console_scripts': [
            'pysteroids = pysteroids.pysteroids:main'
        ]
    },
    packages = find_packages(),
    package_data = {'pysteroids.lib': ['res/*.txt', 'res/sounds/*.wav']},
    install_requires = ['numpy>=1.7.1',
                        'pyglet>1.1.4'],
    dependency_links = ['http://pyglet.googlecode.com/files/' +
                        'pyglet-1.2alpha1.tar.gz#egg=pyglet-1.2'],
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Programming Language :: Python :: 2.7'
    ]
)
