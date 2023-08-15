import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

from mubrary.discogs_download import download_artist

class MusicLibrary:
    def __init__(self, name):
        self.name = name
        self.save_path = Path('')
        self.artists = []
        self.artist_dict = {}

    def add_artist(self, artist_name, alt_names=[], overwrite=False):
        self.artists.append(artist_name)
        while '' in alt_names:
            alt_names.remove('')
        if ('{}.json'.format(artist_name) not in os.listdir(self.save_path/'Raw Downloads')) or overwrite:
            self.artist_dict[artist_name] = download_artist(artist_name, alt_names, self.save_path/'Raw Downloads')
        else:
            with open(self.save_path/'Raw Downloads'/'{}.json'.format(artist_name), 'r') as infile: 
                self.artist_dict[artist_name] = json.load(infile)

    def filter_artist(self, artist):
        release_dict = self.artist_dict[artist]
        cols = ['name','have','want']
        wantage = pd.DataFrame([],columns=cols)
        for name, release in release_dict.items():
            wantage_list = [name,release['community']['have'],
                            release['community']['want']]
            release_wantage = pd.DataFrame([wantage_list],index=[release['year']],
                                            columns=cols)
            wantage = pd.concat([wantage,release_wantage],axis=0)
        wantage = wantage.sort_index()
        page_len = 50
        num_releases = wantage.shape[0]
        for starting_release in np.arange(0,num_releases,page_len):
            page = wantage.iloc[starting_release:min(num_releases,starting_release+page_len)]
            plt.bar(page['name'],page['have'],label='have')
            plt.bar(page['name'],page['have']+page['want'],label='want')
            plt.xticks(rotation = 45) 
            plt.legend()
            plt.show()

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


