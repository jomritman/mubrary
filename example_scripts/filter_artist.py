from mubrary.library import MusicLibrary
from pathlib import Path
from time import time

tic = time()
library_name = 'jombrary'
library_path = '/users/jonathanmartin1/documents/python music'
my_library = MusicLibrary(library_name)
my_library.set_save_path(library_path)
my_library.load_from_json("{}.json".format(library_name))
toc = time()

for artist in my_library.artists:
    my_library.filter_artist(artist, plot_bars=True, plot_counts=True)