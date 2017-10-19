from datetime import datetime

from spotipy import Spotify
import spotipy.util

import pyowm

from models import SQLiteConnection
from models import AudioFeature, Album, Artist, Play, Track

import settings
import util



class SpotifyConnection(object):

    def __init__(self, db_connection):
        token = spotipy.util.prompt_for_user_token(settings.SPOTIFY_USER_NAME,
                                                   scope='user-read-recently-played',
                                                   client_id=settings.SPOTIFY_CLIENT_ID,
                                                   client_secret=settings.SPOTIFY_CLIENT_SECRET,
                                                   redirect_uri=settings.SPOTIFY_REDIRECT_URI)
        self.client = Spotify(auth=token)
        self.db = db_connection

    def _get_image_url_from_response(self, response):
        try:
            return response['images'][0]['url']
        except IndexError:
            pass

    def get_audio_feature(self, track_id):
        audio_feature = self.db.session.query(AudioFeature).get(track_id)

        if not audio_feature:
            response = self.client.audio_features(track_id)[0]
            if response:  # Some tracks do not have audio features
                audio_feature = AudioFeature()
                audio_feature.track_id = track_id
                audio_feature.tempo=response['tempo']
                audio_feature.energy=response['energy']
                audio_feature.valence=response['valence']
                self.db.save_instance(audio_feature)
            else:
                audio_feature = None
        return audio_feature

    def get_artist(self, artist_id):
        artist = self.db.session.query(Artist).get(artist_id)
        if not artist:
            response = self.client.artist(artist_id)
            artist = Artist()
            artist.artist_id=response['id']
            artist.artist_name=response['name']
            artist.image_url=self._get_image_url_from_response(response)
            artist.spotify_url=response['external_urls']['spotify']
            self.db.save_instance(artist)
        return artist

    def get_artists(self, artist_ids):
        artists = []
        for artist_id in artist_ids:
            artists.append(self.get_artist(artist_id))
        return artists

    def get_album(self, album_id):
        album = self.db.session.query(Album).get(album_id)
        if not album:
            response = self.client.album(album_id)
            artist_ids = [a['id'] for a in response['artists']]
            artists = self.get_artists(artist_ids)

            album = Album()
            album.album_id=response['id']
            album.album_name=response['name']
            album.spotify_url=response['external_urls']['spotify']
            # album_genres=response['genres'],
            album.image_url=self._get_image_url_from_response(response)
            album.artists = artists
            self.db.save_instance(album)
        return album

    def get_track(self, track_id):
        track = self.db.session.query(Track).get(track_id)
        if not track:
            response = self.client.track(track_id)
            artist_ids = [a['id'] for a in response['artists']]
            artists = self.get_artists(artist_ids)
            album = self.get_album(response['album']['id'])
            audio_feature = self.get_audio_feature(track_id)

            track = Track()
            track.track_id = track_id
            track.track_name = response['name']
            track.spotify_url = response['external_urls']['spotify']
            track.artists = artists
            track.album = album
            track.audio_feature = audio_feature
            # Save
            self.db.save_instance(track)
        return track

    def _get_play_from_played_at_utc_and_track_id(self, played_at_utc, track_id):
        played_at_utc = util.convert_played_at_from_response_to_datetime(played_at_utc)
        played_at_utc = util.set_timezone_to_datetime(played_at_utc, timezone='UTC')
        played_at_cet = util.convert_datetime_from_timezone_to_timezone(played_at_utc)
        # Play
        play = Play()
        play.played_at_utc = played_at_utc
        play.played_at_utc_timestamp = played_at_utc.timestamp() * 1000
        play.played_at_cet = played_at_cet
        play.played_at_cet_timestamp = played_at_cet.timestamp() * 1000
        play.day = played_at_cet.day
        play.month = played_at_cet.month
        play.year = played_at_cet.year
        play.hour = played_at_cet.hour
        play.minute = played_at_cet.minute
        play.second = played_at_cet.second
        play.day_of_week = played_at_cet.weekday()
        play.week_of_year = played_at_cet.date().isocalendar()[1]
        # Track
        track = self.get_track(track_id)
        play.track = track
        return play

    def _get_plays_from_response(self, response):
        plays = []
        for item in response['items']:
            play = self._get_play_from_played_at_utc_and_track_id(item['played_at'],
                                                                  item['track']['id'])
            plays.append(play)
        return plays

    def get_plays(self, limit=50, after=None):
        plays = []
        response = self.client._get('me/player/recently-played', after=after, limit=limit)
        plays.extend(self._get_plays_from_response(response))

        while 'next' in response:
            response = self.client.next(response)
            plays.extend(self._get_plays_from_response(response))

        return plays
