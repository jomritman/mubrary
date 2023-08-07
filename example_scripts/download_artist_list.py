from mubrary.library import MusicLibrary
from pathlib import Path
import csv

library_name = 'jombrary'
library_path = '/users/jonathanmartin1/documents/python music'

my_library = MusicLibrary(library_name)
my_library.set_save_path(library_path)

# my_library.load_from_json("{}.json".format(library_name))

artist_dict = {}
with open(Path(library_path)/'mubrary artists.csv', 'r') as infile:
    for line in csv.reader(infile,delimiter=','):
        if len(line) > 1:
            artist_dict[line[0]] = line[1:]
        else:
            artist_dict[line[0]] = []
        if '' in artist_dict[line[0]]:
            artist_dict[line[0]].remove('')

for artist, alt_names in artist_dict.items():
    if artist not in my_library.artists:
        my_library.add_artist(artist,alt_names)
    print(artist+'\n')
    for release in list(my_library.artist_dict[artist].keys()):
        print('\t'+release+'\n')

my_library.save_to_json("{}.json".format(library_name))