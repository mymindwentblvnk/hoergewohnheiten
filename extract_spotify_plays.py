import argparse
from datetime import datetime

from spotipy import Spotify
import spotipy.util

from models import Play, Track, Album, Artist, PostgreSQLConnection

import secret_settings
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

    def get_artist(self, artist_id):
        artist = self.db.session.query(Artist).get(artist_id)
        if artist:
            return artist
        else:
            artist_response = self.client.artist(artist_id)
            artist = Artist()
            artist.artist_id = artist_id
            artist.artist_data = artist_response
            self.db.save_instance(artist)
            print("> Artist {} was not in database.".format(artist.artist_data['name']))
            return self.db.session.query(Artist).get(artist_id)

    def get_album(self, album_id):
        album = self.db.session.query(Album).get(album_id)
        if album:
            return album
        else:
            album_response = self.client.album(album_id)
            album = Album()
            album.album_data = album_response
            album.album_id = album_response['id']
            # Artists
            for album_artist_response in album_response['artists']:
                album.artists.append(self.get_artist(album_artist_response['id']))
            self.db.save_instance(album)
            print("> Album {} was not in database.".format(album.album_data['name']))
            return self.db.session.query(Album).get(album_id)

    def get_track(self, track_id):
        track = self.db.session.query(Track).get(track_id)
        if track:
            return track
        else:
            response = self.client.track(track_id)

            track = Track()
            track.track_id = track_id
            track.track_data = response
            # Album
            track.album = self.get_album(response['album']['id'])
            # Artists
            for artist_response in response['artists']:
                track.artists.append(self.get_artist(artist_response['id']))
            # Audio feature
            audio_feature_response = self.client.audio_features(track_id)[0]
            if audio_feature_response:  # Some tracks do not have audio features
                track.audio_feature_data = audio_feature_response
            print("> Track {} was not in database.".format(track.track_data['name']))
            self.db.save_instance(track)
            return self.db.session.query(Track).get(track_id)

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
        print("* Extracting latest plays of {}.".format(self.user_name))
        play_tuples = self._get_play_tuples()

        for played_at, track_id in play_tuples:
            play = self.get_play_from_played_at_utc_and_track_id(played_at, track_id)
            self.db.save_play(play)


class HoergewohnheitenManager(object):

    def __init__(self, spotify_user_data):
        self.spotify = SpotifyConnection(user_data=spotify_user_data)

    def process_hoergewohnheiten(self):
        self.spotify.extract_plays()


def process_hoergewohnheiten(user_name):
    print("***", user_name, "***")
    user_data = secret_settings.SPOTIFY_USERS[user_name]
    mgr = HoergewohnheitenManager(user_data)
    mgr.process_hoergewohnheiten()


if __name__ == '__main__':
    print(util.LOG_HEADER)
    print("Script started at {}.".format(datetime.now()))

    # Argparse
    parser = argparse.ArgumentParser(description='Hoergewohnheiten')
    parser.add_argument('-u', dest='user_name')
    args = parser.parse_args()

    if args.user_name:
        process_hoergewohnheiten(args.user_name)
    else:
        for user_name in secret_settings.SPOTIFY_USERS:
            process_hoergewohnheiten(user_name)

    print("Script finished at {}.".format(datetime.now()))
