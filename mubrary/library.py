import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

from mubrary.discogs_download import download_artist_basics, download_release_details

class MusicLibrary:
    def __init__(self, name):
        self.name = name
        self.save_path = Path('')
        self.artists = []
        self.all_release_basics = {}
        self.filtered_release_basics = {}
        self.filtered_release_details = {}

    def add_artist(self, artist_name, alt_names=[], overwrite=False):
        self.artists.append(artist_name)
        while '' in alt_names:
            alt_names.remove('')
        if ('{}.json'.format(artist_name) not in os.listdir(self.save_path/'Raw Downloads')) or overwrite:
            self.all_release_basics[artist_name] = download_artist_basics(artist_name, alt_names, self.save_path/'Raw Downloads')
        else:
            with open(self.save_path/'Raw Downloads'/'{}.json'.format(artist_name), 'r') as infile: 
                self.all_release_basics[artist_name] = json.load(infile)

    def filter_artist(self, artist, num_want_bins=20, want_thresh=12, plot_bars=False, plot_counts=False):
        release_dict = self.all_release_basics[artist]
        cols = ['name','have','want']
        wantage = pd.DataFrame([],columns=cols)
        for name, release in release_dict.items():
            wantage_list = [name,release['stats']['community']['in_collection'],
                            release['stats']['community']['in_wantlist']]
            release_wantage = pd.DataFrame([wantage_list],index=[release['id']],
                                            columns=cols)
            wantage = pd.concat([wantage,release_wantage],axis=0)
        wantage = wantage.sort_index()
        release_list = wantage['name'].values
        page_len = 20
        num_releases = wantage.shape[0]
        max_wants = 0
        wants = []
        for starting_release in np.arange(0,num_releases,page_len):
            page = wantage.iloc[starting_release:min(num_releases,starting_release+page_len)]
            page_wants = list(np.add(page['have'].values,page['want'].values))
            wants.extend(page_wants)
            max_wants = max(max(page_wants),max_wants)
        for starting_release in np.arange(0,num_releases,page_len):
            page = wantage.iloc[starting_release:min(num_releases,starting_release+page_len)]
            page_wants = list(np.add(page['have'].values,page['want'].values))
            if plot_bars:
                plt.ioff()
                names = list(page['name'].values)
                new_names = []
                for name in names:
                    # type = self.filtered_release_details[artist][name]['formats'][0]['descriptions'][0]
                    # date = self.filtered_release_details[artist][name]['released_formatted']
                    if len(name) > 30: #+len(type)
                        new_name = name[:(30)]+'...'#-len(type)
                    else:
                        new_name = name
                    # new_name += " ["+type+"] - "+date[-4:]
                    new_names.append(new_name)
                ax = plt.gca()
                ax.barh(new_names,page_wants,label='want')
                ax.barh(new_names,page['have'].values,label='have')
                ax.legend()
                ax.set_position([.5,.05,.49,.94])
                ax.plot(np.exp(np.log(max_wants)*want_thresh/num_want_bins)*np.ones(2),[-1,page_len],'r-')
                ax.set_xscale('log')
                plt.show()

        if max_wants > 0:
            want_bin_int = np.log(max_wants)/float(num_want_bins)
            want_bin_ends = np.arange(0,np.log(max_wants)+want_bin_int,want_bin_int)
            want_bin_mids = []
            want_bin_counts = []
            want_bin_idx_dict = {}
            for want_bin_idx, want_bin_start in enumerate(want_bin_ends[:-1]):
                want_bin_end = want_bin_ends[want_bin_idx+1]
                want_bin_mids.append(np.exp((want_bin_start+want_bin_end)/2))
                want_bin_idxs = np.argwhere(np.logical_and(np.greater_equal(np.log(wants),want_bin_start),np.less_equal(np.log(wants),want_bin_end)))
                want_bin_idxs = np.squeeze(want_bin_idxs, axis=1)

                want_bin_count = len(want_bin_idxs)
                want_bin_counts.append(want_bin_count)
                want_bin_idx_dict[want_bin_end] = want_bin_idxs
            if plot_counts:
                plt.semilogx(want_bin_mids,want_bin_counts)
                plt.title(artist)
                plt.show()

            filtered_release_dict = {}
            for release_bin in want_bin_ends[want_thresh:]:
                release_idxs = want_bin_idx_dict[release_bin]
                for release_idx in release_idxs:
                    filtered_release_dict[release_list[release_idx]] = release_dict[release_list[release_idx]]

            self.filtered_release_basics[artist] = filtered_release_dict

    def get_artist_details(self, artist, overwrite=False):

        if artist in list(self.filtered_release_basics.keys()):
            release_dict = self.filtered_release_basics[artist]
            if ('{} Details.json'.format(artist) not in os.listdir(self.save_path/'Raw Downloads')) or overwrite: 
                filtered_release_dict = {}
                for release in release_dict.values():
                    filtered_release_dict[(release['title'])] = download_release_details(release)
                with open(self.save_path/'Raw Downloads'/'{} Details.json'.format(artist), 'w') as outfile:
                    json.dump(filtered_release_dict, outfile)
            else:
                with open(self.save_path/'Raw Downloads'/'{} Details.json'.format(artist), 'r') as infile:
                    filtered_release_dict = json.load(infile)

            self.filtered_release_details[artist] = filtered_release_dict

    def set_save_path(self, path):
        if type(path) is not Path:
            path = Path(path)
        self.save_path = path

    def save_to_json(self, filename):
        all_dict = {'artists':self.artists,
                    'arb':self.all_release_basics,
                    'frb':self.filtered_release_basics,
                    'frd':self.filtered_release_details}
        with open(self.save_path/"Libraries"/filename, "w") as outfile:
            json.dump(all_dict, outfile)

    def load_from_json(self, filename):
        with open(self.save_path/"Libraries"/filename, "r") as infile:
            all_dict = json.load(infile)
            self.artists = all_dict['artists']
            self.all_release_basics = all_dict['arb']
            self.filtered_release_basics = all_dict['frb']
            self.filtered_release_details = all_dict['frd']

