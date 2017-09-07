from spotipy import Spotify
import spotipy.util

import pyowm

import settings

from datetime import datetime


def convert_played_at_from_response_to_datetime(played_at):
    try:
        return datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        # For the single moment where the played at time hits a full second
        return datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%SZ')


class AudioFeature(object):

    def __init__(self, tempo='', energy='', valence=''):
        self.tempo = tempo
        self.energy = energy
        self.valence = valence


class Album(object):

    def __init__(self, album_id, album_name, label, album_genres):
        self.album_id = album_id
        self.album_name = album_name
        self.label = label
        self.album_genres = album_genres


class Artist(object):

    def __init__(self, artist_id, artist_name, artist_genres):
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.artist_genres = artist_genres


class Track(object):

    def __init__(self, track_id, track_name, artist, album, audio_feature, played_at):
        self.track_id = track_id
        self.track_name = track_name
        self.artist = artist
        self.album = album
        self.audio_feature = audio_feature
        self.played_at = played_at
    

class SpotifyConnection(object):

    def __init__(self):
        token = spotipy.util.prompt_for_user_token(settings.SPOTIFY_USER_NAME,
                                                   scope='user-read-recently-played',
                                                   client_id=settings.SPOTIFY_CLIENT_ID,
                                                   client_secret=settings.SPOTIFY_CLIENT_SECRET,
                                                   redirect_uri=settings.SPOTIFY_REDIRECT_URI)
        self.client = Spotify(auth=token)
        self.album_cache = {}
        self.artist_cache = {}
        self.audio_feature_cache = {}

    def get_audio_feature(self, track_id):
        if track_id not in self.audio_feature_cache:
            response = self.client.audio_features(track_id)[0]
            if response:  # Some tracks do not have audio features
                audio_feature = AudioFeature(tempo=response['tempo'],
                                             energy=response['energy'],
                                             valence=response['valence'])
                self.audio_feature_cache[track_id] = audio_feature
            else:
                return AudioFeature()
        return self.audio_feature_cache[track_id]

    def get_album(self, album_id):
        if album_id not in self.album_cache:
            response = self.client.album(album_id)
            album = Album(album_id=response['id'],
                          album_name=response['name'],
                          label=response['label'],
                          album_genres=response['genres'])
            self.album_cache[album_id] = album
        return self.album_cache[album_id]

    def get_artist(self, artist_id):
        if artist_id not in self.artist_cache:
            response = self.client.artist(artist_id)
            artist = Artist(artist_id=response['id'],
                            artist_name=response['name'],
                            artist_genres=response['genres'])
            self.artist_cache[artist_id] = artist
        return self.artist_cache[artist_id]

    def _get_tracks_from_response(self, response):
        tracks = []
        for item in response['items']:
            played_at_as_utc = item['played_at']
            played_at = convert_played_at_from_response_to_datetime(played_at_as_utc)

            response_track = item['track']

            album = self.get_album(response_track['album']['id'])
            artist = self.get_artist(response_track['artists'][0]['id'])
            audio_feature = self.get_audio_feature(response_track['id'])
            track = Track(track_id=response_track['id'],
                          track_name=response_track['name'],
                          artist=artist,
                          album=album,
                          audio_feature=audio_feature,
                          played_at=played_at)
            tracks.append(track)
        return tracks
        
    def get_recently_played_tracks(self, limit=50, after=None):
        tracks = []
        response = self.client._get('me/player/recently-played', after=after, limit=limit)
        tracks.extend(self._get_tracks_from_response(response))

        while 'next' in response:
            response = self.client.next(response)
            tracks.extend(self._get_tracks_from_response(response))
        return tracks


class Weather(object):

    def __init__(self, temperature='', status=''):
        self.temperature = temperature
        self.status = status


class OWMConnection(object):

    def __init__(self):
        self.owm = pyowm.OWM(settings.OPEN_WEATHER_MAP_API_KEY)

    def get_weather(self):
        try:
            observation = self.owm.weather_at_id(settings.OPEN_WATHER_MAP_NUREMBERG_ID)
            weather = observation.get_weather()
            temperature = weather.get_temperature(unit='celsius')['temp']
            weather_status = weather.get_detailed_status()
            return Weather(temperature=temperature,
                           status=weather_status)
        except:
            return Weather()