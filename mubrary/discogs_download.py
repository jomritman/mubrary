import pandas as pd
import json
from pathlib import Path
import discogs_client
from time import sleep

"""
discogs_download.py

This is a library of functions that can be used to download information about artists and their releases
using the discogs.com API. Requires only very common python packages seen above as well as discogs_client

"""

def download_artist_basics(artist_name, alt_name_list = [], save_path = Path('')):

    '''
    Downloads basic information about an artist and saves it to a .json file and returns it as a dict
    Required input:     artist_name (str) - the name of the artist
    Optional inputs:    alt_name_list (list) - a list of strs of possible alternate names
                                                ("The" at the beginning, "&" instead of "and", etc.)
                        save_path - str or Path of where to save the .json file
    '''
    
    if type(save_path) is str:
        save_path = Path(save_path) 

    if len(alt_name_list) == 0:
        alt_name_list = [artist_name]
    
    client_name = 'jomritman_mubrary'
    max_pages = 10
    max_tries = 5

    # Read in token
    with open('token.txt', 'r') as file:
        user_token = file.read()

    dc = discogs_client.Client(client_name,user_token=user_token)

    artist_dict = {}
    release_names = []
    for search_artist in alt_name_list:
        results = dc.search(search_artist, type='artist')
        if len(results) > 0:
            artist_id = results[0].data['id']
            releases_url = 'https://api.discogs.com/artists/{}/releases?page=1&per_page=100'.format(artist_id)
            page = 1
            while releases_url is not None:
                tries = 0
                while tries < max_tries:
                    try:
                        release_info = dc._get(releases_url)
                        for release in release_info['releases']:
                            if release['artist'] in alt_name_list:
                                release_name = release['title']
                                if release_name not in release_names:
                                    if release['type'] == 'master':
                                        release_names.append(release_name)
                                        artist_dict[release_name] = release
                        tries = max_tries
                    except:
                        tries += 1
                        if tries == max_tries:
                            raise ConnectionError('Maximum attempts to query discogs.com exceeded!')
                if (page == release_info['pagination']['pages']) or (page == max_pages):
                    releases_url = None
                else:
                    page += 1
                    releases_url = releases_url = 'https://api.discogs.com/artists/{}/releases?page={}&per_page=100'.format(artist_id,page)

    with open(save_path/"{}.json".format(artist_name), "w") as outfile:
        json.dump(artist_dict, outfile)

    return artist_dict

def download_release_details(release):

    release_url = 'https://api.discogs.com/releases/{}'.format(str(release['main_release']))
    client_name = 'jomritman_mubrary'
    max_pages = 10
    max_tries = 5

    # Read in token
    with open('token.txt', 'r') as file:
        user_token = file.read()

    dc = discogs_client.Client(client_name,user_token=user_token)
    tries = 0
    while tries < max_tries:
        try:
            release_details = dc._get(release_url)
            tries = max_tries
        except:
            tries += 1

    return release_details