import json
import discogs_client
from time import sleep
from pathlib import Path

client_name = 'jomritman_mubrary'

base_dir = Path(__file__).parent/'..'

# Read in token
with open(base_dir/'token.txt', 'r') as file:
    user_token = file.read()

dc = discogs_client.Client(client_name,user_token=user_token)

artist_dict = {'Shellac':['Shellac'],
                'The Chats':['The Chats'],
                'Frank Zappa':['Frank Zappa','The Mothers of Invention']}
for artist_name, search_artists in artist_dict.items():
    release_dict = {artist_name:{}}
    release_names = []
    for search_artist in search_artists:
        results = dc.search(search_artist, type='artist')
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
                    release_dict[artist_name][release_name] = release_obj
                    sleep(1)

    with open(base_dir/"raw_downloads"/"{}.json".format(artist_name), "w") as outfile:
        json.dump(release_dict, outfile)

# for result_num in range(results.count):
#     release = results[result_num]
#     is_them = False
#     for artist in release.artists:
#         if not is_them:
#             is_them = search_artist in artist.data['name']
#     if is_them:
#         release_name = release.data['title']
#         if release_name not in release_names:
#             release_names.append(release_name)           
        
columns = {}