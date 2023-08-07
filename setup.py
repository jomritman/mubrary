from setuptools import setup

setup(
    name='mubrary',
    version='0.1',
    description='Music Library Tool',
    url='https://github.com/jomritman/mubrary',
    author='jomritman',
    author_email='jomritman@gmail.com',
    install_requires=[
        'python3-discogs-client',
        ],
    packages=[
        'mubrary',
        ]
)