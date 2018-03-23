import json
import os
import requests
import time

import spotipy.util as util

SPOTIFY_API = 'https://api.spotify.com/v1'
SPOTIFY_API_ME = SPOTIFY_API + '/me'
SPOTIFY_USER = 'acsspotify'
SCOPES = 'user-library-read,user-read-recently-played,user-top-read'
SCOPE_LIB = 'user-library-read'
SCOPE_HISTORY = 'user-read-recently-played'
SCOPE_TOP = 'user-top-read'

TOKEN = 'token'
TOKEN_LIB = 'token-lib'
TOKEN_HISTORY = 'token-history'
TOKEN_TOP = 'token-top'


def collect_tokens(user):
    """
    Collect tokens for SCOPE and SCOPE_HISTORY Spotify scopes

    :param user: Spotify user for getting the tokens
    :return: the token and token_history for this user
    """

    # First step is to configure the env for asking for tokens
    with open("app-credentials.json") as file:
        os.environ.update(json.load(file))

    # Access tokens expire after one hour. This expiry time is set on Spotify's side and can't be changed by the client
    # So we ask for a new token if we don't have a recent one

    refresh_token = False

    try:
        # If tokens are older than 1h (3600s) we must refresh them
        if int(time.time() - int(os.path.getmtime(TOKEN))) > 3600:
            refresh_token = True
    except Exception as ex:
        refresh_token = True

    if refresh_token:
        print("Refreshing the token ... be patient")
        token = util.prompt_for_user_token(SPOTIFY_USER, SCOPES)
        with open(TOKEN, "w") as ftoken:
            ftoken.write(token)
    else:
        with open(TOKEN, "r") as ftoken:
            token = ftoken.read()

    return token



def find_playlists(token):
    """
    Get the playlists for the user

    :param token: user token for getting her playlists
    :return: 
    """
    headers = {"Authorization": "Bearer %s" % token}

    res = requests.get(SPOTIFY_API_ME + "/playlists", headers=headers)
    res.raise_for_status()

    playlists = res.json()

    print(playlists['items'][0])


def find_recently_played(token_history):
    """ Find the last 50 find_recently_played tracks by the user """

    # Right now the API from Spotify only allows to get the 50 tracks last played
    limit = "50"

    headers = {"Authorization": "Bearer %s" % token_history}

    history_url = SPOTIFY_API_ME + "/player/recently-played?limit=%s" % limit

    res = requests.get(history_url, headers=headers)

    res.raise_for_status()

    recent_tracks = res.json()


    for track in recent_tracks['items']:
        print(track['track'], ":", ['name'], track['track']['artists'][0]['name'])

def find_tops(token_top, kind='tracks'):
    """
    Find the top tracks or artists
    :param token_top: Token for accessing the Top API
    :return:
    """
    headers = {"Authorization": "Bearer %s" % token_top}
    limit = "50"
    history_url = SPOTIFY_API_ME + "/top/%s?limit=%s" % (kind, limit)

    res = requests.get(history_url, headers=headers)
    res.raise_for_status()
    top_tracks = res.json()

    for track in top_tracks['items']:
        print(track['name'], ":", track['artists'][0]['name'])


if __name__ == '__main__':
    token = collect_tokens(SPOTIFY_USER)
    find_tops(token)
    find_recently_played(token)

