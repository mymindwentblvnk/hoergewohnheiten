from datetime import datetime

from spotipy import Spotify
import spotipy.util

import pyowm

from models import SQLiteConnection
from models import AudioFeature, Album, Artist, Play, Track

import settings
import util



def convert_played_at_from_response_to_datetime(played_at):
    try:
        return datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        # For the single moment where the played at time hits a full second
        return datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%SZ')


class SpotifyConnection(object):

    def __init__(self):
        token = spotipy.util.prompt_for_user_token(settings.SPOTIFY_USER_NAME,
                                                   scope='user-read-recently-played',
                                                   client_id=settings.SPOTIFY_CLIENT_ID,
                                                   client_secret=settings.SPOTIFY_CLIENT_SECRET,
                                                   redirect_uri=settings.SPOTIFY_REDIRECT_URI)
        self.client = Spotify(auth=token)
        db_path = '{}/{}'.format(settings.PATH_TO_DATA_REPO, settings.DB_FILE_NAME)
        self.db = SQLiteConnection(db_path)

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
                audio_feature.tempo=response['tempo']
                audio_feature.energy=response['energy']
                audio_feature.valence=response['valence']
            else:
                audio_feature = None
        return audio_feature

    def get_artist(self, artist_id):
        if artist_id not in self.artist_cache:
            response = self.client.artist(artist_id)
            artist = Artist(artist_id=response['id'],
                            artist_name=response['name'],
                            artist_picture_url=self._get_image_url_from_response(response),
                            artist_url=response['external_urls']['spotify'])
            self.artist_cache[artist_id] = artist
        return self.artist_cache[artist_id]

    def get_album(self, album_id):
        album = self.db.session.query(Album).get(album_id)
        if not album:
            response = self.client.album(album_id)
            # artist = self.get_artist(response['artists'][0]['id'])
            album = Album()
            album.album_id=response['id'],
            album.album_name=response['name'],
            album.spotify_url=response['external_urls']['spotify'],
            # album_genres=response['genres'],
            album.image_url=self._get_image_url_from_response(response),
            # artist=artist)
            self.db.save_instance(album)
        return album

    def get_track(self, track_id):
        track = self.db.session.query(Track).get(track_id)
        if not track:
            response = self.client.track(track_id)
            # artist = self.get_artist(response['artists'][0]['id'])
            album = self.get_album(response['album']['id'])
            audio_feature = self.get_audio_feature(track_id)

            track = Track()
            track.track_id = track_id
            track.track_name = response['name']
            track.spotify_url = response['external_urls']['spotify']
            # track.artist = artist
            track.album = album
            track.audio_feature = audio_feature
            # Save
            self.db.save_instance(track)
        return track

    # def get_tracks(self, track_ids):
    #     tracks = []
    #     for chunk in util.chunks(track_ids, 50):
    #         responses = self.client.tracks(chunk)
    #         for response in responses['tracks']:
    #             track_id = response['id']
    #             artist = self.get_artist(response['artists'][0]['id'])
    #             album = self.get_album(response['album']['id'])
    #             track = Track(track_id=track_id,
    #                           track_name=response['name'],
    #                           track_url=response['external_urls']['spotify'],
    #                           artist=artist,
    #                           album=album)
    #             self.track_cache[track_id] = track
    #             tracks.append(track)
    #     return tracks
    #
    def _get_play_from_response(self, response):
        tracks = []
        for item in response['items']:
            played_at_utc = convert_played_at_from_response_to_datetime(item['played_at'])
            played_at_cet = util.convert_datetime_utc_to_cet(played_at_utc)
            # Play
            play = Play()
            play.played_at_utc = played_at_utc
            play.played_at_cet = played_at_cet
            play.day = played_at_cet.day
            play.month = played_at_cet.month
            play.year = played_at_cet.year
            play.minute = played_at_cet.minute
            play.second = played_at_cet.second
            play.day_of_week = played_at_cet.weekday()
            play.week_of_year = played_at_cet.date().isocalendar()[1]
            # Track
            track = self.get_track(item['track']['id'])
            play.track = track
            plays.append(play)
        return plays

    def get_plays(self, limit=50, after=None):
        plays = []
        response = self.client._get('me/player/recently-played', after=after, limit=limit)
        plays.extend(self.get_plays(response))

        while 'next' in response:
            response = self.client.next(response)
            plays.extend(self.get_plays(response))
        return plays
