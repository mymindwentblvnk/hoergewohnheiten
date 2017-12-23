from datetime import datetime

from spotipy import Spotify
import spotipy.util

from models import Play, Track, PostgreSQLConnection

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

    def get_track(self, track_id):
        track = self.db.session.query(Track).get(track_id)
        if not track:
            response = self.client.track(track_id)
            album_response = self.client.album(response['album']['id'])

            track = Track()
            track.track_id = track_id
            track.track_data = response
            track.album_data = album_response
            # Audio feature
            audio_feature_response = self.client.audio_features(track_id)[0]
            if audio_feature_response:  # Some tracks do not have audio features
                track.audio_feature_data = audio_feature_response
            # Save
            self.db.save_instance(track)
            print("> Track {} was not in database. Now is.".format(track.track_data['name']))
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
