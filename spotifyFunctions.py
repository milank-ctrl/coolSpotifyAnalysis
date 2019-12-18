
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pw
import pandas as pd
from requests import exceptions

client_id = pw.client_id
client_secret = pw.client_secret
redirect_uri = pw.redirect_uri
user_id = pw.user_id
username = pw.username


def auth(user_id, client_id, client_secret, redirect_uri):   
    token = util.prompt_for_user_token(user_id,
                                       'playlist-read-collaborative',
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri=redirect_uri)
    return token

token = auth(user_id, client_id, client_secret, redirect_uri)

sp = spotipy.Spotify(auth=token)

def getPlaylists(userName, token):
    
    sp = spotipy.Spotify(auth=token)
    
    playlists = sp.user_playlists(userName)
    playlist_lst = []

    for playlist in playlists['items']:
        playlist_dict = {}
        playlist_dict['playlistName'] = playlist['name']
        playlist_dict['playlistId'] = playlist['id']
        playlist_dict['playlistHref'] = playlist['href']
        playlist_dict['playlisOwner'] = playlist['owner']['display_name']
        playlist_dict['playlisPublic'] = playlist['public']
        playlist_dict['tracksHref'] = playlist['tracks']['href']
        playlist_dict['tracksCount'] = playlist['tracks']['total']

        playlist_lst.append(playlist_dict)
    
    return playlist_lst

getPlaylists('kocza.milan', token)


def getTracks(playlistId, token):
    
    sp = spotipy.Spotify(auth=token)
    track_lst = []
    sourcePlaylist = sp.user_playlist(user=username, playlist_id=playlistId)
    tracks = sourcePlaylist['tracks']
    
    while True:
        sp = spotipy.Spotify(auth=token)
        for track in tracks['items']:
            
            track_dict = {}

            artistId = track['track']['album']['artists'][0]['id']
            artistInfo = sp.artist(artistId)

            songId = track['track']['id']
            audioInfo = sp.audio_features(songId)[0]

            track_dict['playListId'] = playlistId
            #track_dict['playListName'] = playlist["playlistName"]
            track_dict['added_at'] = track['added_at']
            track_dict['artisId'] = artistId
            track_dict['artisName'] = track['track']['album']['artists'][0]['name']
            track_dict['artisType'] = track['track']['album']['artists'][0]['type']
            track_dict['genre'] = artistInfo['genres']
            track_dict['artistPopularity'] = artistInfo['popularity']
            track_dict['albumId'] = track['track']['album']['id']
            track_dict['albumName'] = track['track']['album']['name']
            track_dict['albumReleaseDate'] = track['track']['album']['release_date']
            track_dict['albumImage'] = track['track']['album']['images'][0]['url']
            track_dict['songId'] = songId
            track_dict['songTitle'] = track['track']['name']
            track_dict['songSample'] = track['track']['preview_url']
            track_dict['songPopularity'] = track['track']['popularity']
            track_dict['songDurationMs'] = track['track']['duration_ms']
            track_dict['danceability'] = audioInfo['danceability']
            track_dict['energy'] = audioInfo['energy']
            track_dict['loudness'] = audioInfo['loudness']
            track_dict['mode'] = audioInfo['mode']
            track_dict['speechiness'] = audioInfo['speechiness']
            track_dict['acousticness'] = audioInfo['acousticness']
            track_dict['instrumentalness'] = audioInfo['instrumentalness']
            track_dict['liveness'] = audioInfo['liveness']
            track_dict['valence'] = audioInfo['valence']
            track_dict['tempo'] = audioInfo['tempo'] 

            track_lst.append(track_dict)

        if tracks['next'] == None:
            break

        tracks = sp._get(tracks['next'])
    
    return track_lst


df = pd.DataFrame.from_dict(getTracks('79huJWUFredOrxzcXdCGYo', token))

