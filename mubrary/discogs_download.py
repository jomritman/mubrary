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
            releases_url = 'https://api.discogs.com/artists/{}/releases'.format(artist_id)
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

    with open(save_path/"{}.json".format(artist_name), "w") as outfile:
        json.dump(release_dict, outfile)

    return release_dict