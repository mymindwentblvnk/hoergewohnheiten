from datetime import datetime

from spotipy import Spotify
import spotipy.util

from models import Album, Artist, Play, Track, PostgreSQLConnection

import settings
import util


class SpotifyConnection(object):

    def __init__(self, user_data):
        self.user_name = user_data['user_name']
        token = spotipy.util.prompt_for_user_token(self.user_name,
                                                   scope='user-read-recently-played',
                                                   client_id=user_data['client_id'],
                                                   client_secret=user_data['client_secret'],
                                                   redirect_uri=user_data['redirect_uri'])
        self.client = Spotify(auth=token)
        self.db = self.init_db()

    def init_db(self):
        return PostgreSQLConnection()

    def _get_image_url_from_response(self, response):
        try:
            return response['images'][0]['url']
        except IndexError:
            pass

    def get_artist(self, artist_id):
        artist = self.db.session.query(Artist).get(artist_id)
        if not artist:
            response = self.client.artist(artist_id)
            artist = Artist()
            artist.artist_id = response['id']
            artist.artist_name = response['name']
            artist.image_url = self._get_image_url_from_response(response)
            artist.spotify_url = response['external_urls']['spotify']
            self.db.save_instance(artist)
            print("> Artist {} was not in database. Now is.".format(artist.artist_name))
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
            album.album_id = response['id']
            album.album_name = response['name']
            album.spotify_url = response['external_urls']['spotify']
            album.image_url = self._get_image_url_from_response(response)
            album.artists = artists
            self.db.save_instance(album)
            print("> Album {} was not in database. Now is.".format(album.album_name))
        return album

    def get_track(self, track_id):
        track = self.db.session.query(Track).get(track_id)
        if not track:
            response = self.client.track(track_id)
            artist_ids = [a['id'] for a in response['artists']]
            artists = self.get_artists(artist_ids)
            album = self.get_album(response['album']['id'])

            track = Track()
            track.track_id = track_id
            track.track_name = response['name']
            track.spotify_url = response['external_urls']['spotify']
            track.artists = artists
            track.album = album
            # Audio feature
            audio_feature_response = self.client.audio_features(track_id)[0]
            if audio_feature_response:  # Some tracks do not have audio features
                track.tempo = audio_feature_response['tempo']
                track.energy = audio_feature_response['energy']
                track.valence = audio_feature_response['valence']
            # Save
            self.db.save_instance(track)
            print("> Track {} was not in database. Now is.".format(track.track_name))
        return track

    def get_play_from_played_at_utc_and_track_id(self, played_at_utc, track_id):
        played_at_utc = util.convert_played_at_from_response_to_datetime(played_at_utc)
        played_at_utc = util.set_timezone_to_datetime(played_at_utc, timezone='UTC')
        played_at_cet = util.convert_datetime_from_timezone_to_timezone(played_at_utc)
        # Play
        play = Play()
        play.user_name = self.user_name
        play.played_at_utc_timestamp = played_at_utc.timestamp() * 1000
        play.played_at_utc = played_at_utc
        play.played_at_cet = played_at_cet
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
        play.track_id = track_id
        return play

    def _get_play_tuples_from_response(self, response):
        plays = []
        for item in response['items']:
            play_tuple = (item['played_at'], item['track']['id'])
            plays.append(play_tuple)
        return plays

    def _get_play_tuples(self, limit=50, after=None):
        play_tuples = []
        response = self.client._get('me/player/recently-played', after=after, limit=limit)
        play_tuples.extend(self._get_play_tuples_from_response(response))

        while 'next' in response:
            response = self.client.next(response)
            play_tuples.extend(self._get_play_tuples_from_response(response))

        return play_tuples

    def extract_plays(self):
        print("* Extracting latest plays of {} from Spotify API.".format(self.user_name))
        play_tuples = self._get_play_tuples()

        plays = []
        for played_at, track_id in play_tuples:
            play = self.get_play_from_played_at_utc_and_track_id(played_at, track_id)
            plays.append(play)

        print("* Saving plays to database.")
        self.db.save_instance(plays)
