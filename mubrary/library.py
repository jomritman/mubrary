import os
import json
from pathlib import Path

from mubrary.discogs_download import download_artist

class MusicLibrary:
    def __init__(self, name):
        self.name = name
        self.save_path = Path('')
        self.artists = []
        self.artist_dict = {}

    def add_artist(self, artist_name, alt_names=[], overwrite=False):
        self.artists.append(artist_name)
        if ('{}.json'.format(artist_name) not in os.listdir(self.save_path/'Raw Downloads')) or overwrite:
            self.artist_dict[artist_name] = download_artist(artist_name, alt_names, self.save_path/'Raw Downloads')
        else:
            with open(self.save_path/'Raw Downloads'/'{}.json'.format(artist_name), 'r') as infile: 
                self.artist_dict[artist_name] = json.load(infile)

    def set_save_path(self, path):
        if type(path) is not Path:
            path = Path(path)
        self.save_path = path

    def save_to_json(self, filename):
        with open(self.save_path/"Libraries"/filename, "w") as outfile:
            json.dump(self.artist_dict, outfile)

    def load_from_json(self, filename):
        with open(self.save_path/"Libraries"/filename, "r") as infile:
            self.artist_dict = json.load(infile)
            self.artists = list(self.artist_dict.keys())


