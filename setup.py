from setuptools import setup, find_packages

setup(
    name='pysteroids',
    version='1.0',
    description='A clone of the game Asteroids implemented in Python',
    author='Max Mays',
    author_email='wmays@max-mays.com',
    url='https://github.com/Cheeser12/pysteroids',
    packages=find_packages(),
    package_data={'lib': ['res/*.txt'],}
)