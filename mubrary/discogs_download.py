import pandas as pd
import json
from pathlib import Path
import discogs_client
from time import sleep

def download_artist(artist_name, alt_name_list = [], save_path = Path('')):

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

    release_dict = {}
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
                            if search_artist in release['artist']:
                                release_name = release['title']
                                if release_name not in release_names:
                                    release_names.append(release_name)
                                    if 'main_release' in release.keys():
                                        release_id = release['main_release']
                                    else:
                                        release_id = release['id']
                                    release_url = 'https://api.discogs.com/releases/{}'.format(release_id)
                                    release_obj = dc._get(release_url)
                                    release_dict[release_name] = release_obj
                                    sleep(1)
                        tries = max_tries
                    except:
                        tries += 1
                if (page == release_info['pagination']['pages']) or (page == max_pages):
                    releases_url = None
                else:
                    page += 1
                    releases_url = releases_url = 'https://api.discogs.com/artists/{}/releases?page={}&per_page=100'.format(artist_id,page)

    with open(save_path/"{}.json".format(artist_name), "w") as outfile:
        json.dump(release_dict, outfile)

    return release_dict