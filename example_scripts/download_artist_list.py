from mubrary.library import MusicLibrary
from pathlib import Path
import csv
import os

library_name = 'jombrary_ATDI'
library_path = '/users/jonathanmartin1/documents/python music'

my_library = MusicLibrary(library_name)
my_library.set_save_path(library_path)

if "{}.json".format(library_name) not in os.listdir(Path(library_path)/'Libraries'):
    my_library.save_to_json("{}.json".format(library_name))

artist_dict = {}
with open(Path(library_path)/'mubrary artists.csv', 'r') as infile:
    for line in csv.reader(infile,delimiter=','):
        if len(line) > 1:
            artist_dict[line[0]] = line[1:]
        else:
            artist_dict[line[0]] = []
        if '' in artist_dict[line[0]]:
            artist_dict[line[0]].remove('')

my_library.load_from_json("{}.json".format(library_name))

for artist, alt_names in artist_dict.items():

    if artist not in my_library.artists:
        my_library.add_artist(artist,alt_names)
        my_library.filter_artist(artist, want_thresh=8)
        print(artist+'\n')
        if artist in list(my_library.filtered_release_basics.keys()):
            for release in list(my_library.filtered_release_basics[artist].values()):
                print('\t'+release['title']+', want: '+str(release['stats']['community']['in_wantlist'])+', have: '+str(release['stats']['community']['in_collection'])+'\n')
        my_library.get_artist_details(artist)
my_library.save_to_json("{}.json".format(library_name))