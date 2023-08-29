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

    def filter_artist(self, artist, plot_bars=False):
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
        page_len = 20
        num_releases = wantage.shape[0]
        max_wants = 0
        wants = []
        for starting_release in np.arange(0,num_releases,page_len):
            page = wantage.iloc[starting_release:min(num_releases,starting_release+page_len)]
            page_wants = list(np.add(page['have'].values,page['want'].values))
            wants.extend(page_wants)
            max_wants = max(max(page_wants),max_wants)
            if plot_bars:
                plt.bar(page['name'],page_wants,label='want')
                plt.bar(page['name'],page['have'].values,label='have')
                plt.xticks(rotation = 45) 
                plt.legend()
                plt.show()
        num_want_bins = 20
        want_bin_int = np.log(max_wants)/float(num_want_bins)
        want_bin_ends = np.arange(0,np.log(max_wants)+want_bin_int,want_bin_int)
        want_bin_mids = []
        want_bin_counts = []
        want_bin_idx_dict = {}
        for want_bin_idx, want_bin_start in enumerate(want_bin_ends[:-1]):
            want_bin_end = want_bin_ends[want_bin_idx+1]
            want_bin_mids.append(np.exp((want_bin_start+want_bin_end)/2))
            want_bin_idxs = np.argwhere(np.logical_and(np.greater_equal(np.log(wants),want_bin_start),np.less_equal(np.log(wants),want_bin_end)))
            want_bin_count = len(want_bin_idxs)
            want_bin_counts.append(want_bin_count)
            want_bin_idx_dict[want_bin_end] = want_bin_idxs
        plt.semilogx(want_bin_mids,want_bin_counts)
        plt.title(artist)
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


