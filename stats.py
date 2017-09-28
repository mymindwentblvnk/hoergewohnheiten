import pandas as pd
from glob import glob

from connections import OWMConnection, SpotifyConnection

import settings
import util


SPOTIFY = SpotifyConnection()


class HoergewohnheitenStatsMixin(object):

    last_n_tracks = 20

    def _load_csv_files(self, year=None, month=None):
        if not year and not month:  # All time
            csv_file_paths = glob('{}/[2-9][0-9][0-9][0-9]-[0-1][0-9].csv'.format(settings.PATH_TO_DATA_REPO))
        elif year and not month:  # Year
            csv_file_paths = glob('{}/{}-[0-1][0-9].csv'.format(settings.PATH_TO_DATA_REPO, year))
        elif year and month:  # Month
            csv_file_paths = glob('{}/{}-{}.csv'.format(settings.PATH_TO_DATA_REPO, year, util.pad_number(month)))

        data_frames = []
        for index, path in enumerate(csv_file_paths, 1):
            frame = pd.read_csv(path)
            data_frames.append(frame)
        return pd.concat(data_frames, ignore_index=True)

    def _get_times(self):
        times = pd.to_datetime(self.data_frame.played_at_as_utc)
        return times + pd.Timedelta('{}:00:00'.format(util.pad_number(settings.HOURS_FROM_UTC)))

    def last_played_tracks(self):
        result = {}
        latest_plays = self.data_frame.tail(self.last_n_tracks)
        for index in range(self.last_n_tracks):
            played_at_as_utc = latest_plays.iloc[index]['played_at_as_utc']
            track_id = latest_plays.iloc[index]['track_id']
            track = self.spotify.get_track(track_id)

            result_index = self.last_n_tracks - index  # Puts latest play on index 1 and so forth

            result[result_index] = {}
            result[result_index]['played_at_as_utc'] = played_at_as_utc
            result[result_index]['id'] = track.track_id
            result[result_index]['name'] = track.track_name
            result[result_index]['spotify_url'] = track.track_url
            result[result_index]['artist'] = {}
            result[result_index]['artist']['id'] = track.artist.artist_id
            result[result_index]['artist']['name'] = track.artist.artist_name
            result[result_index]['artist']['image_url'] = track.artist.artist_picture_url
            result[result_index]['artist']['spotify_url'] = track.artist.artist_url
            result[result_index]['album'] = {}
            result[result_index]['album']['id'] = track.album.album_id
            result[result_index]['album']['name'] = track.album.album_name
            result[result_index]['album']['image_url'] = track.album.cover_url
            result[result_index]['album']['spotify_url'] = track.album.album_url
        return result

    def top_tracks(self):
        result = {}
        top_tracks = self.data_frame.groupby('track_id').size().sort_values(ascending=False)[:self.top_n]
        for index, track_id in enumerate(top_tracks.keys(), 1):
            track = self.spotify.get_track(track_id)
            result[index] = {}
            result[index]['plays'] = int(top_tracks[track_id])
            result[index]['id'] = track.track_id
            result[index]['name'] = track.track_name
            result[index]['spotify_url'] = track.track_url
            result[index]['artist'] = {}
            result[index]['artist']['id'] = track.artist.artist_id
            result[index]['artist']['name'] = track.artist.artist_name
            result[index]['artist']['image_url'] = track.artist.artist_picture_url
            result[index]['artist']['spotify_url'] = track.artist.artist_url
            result[index]['album'] = {}
            result[index]['album']['id'] = track.album.album_id
            result[index]['album']['name'] = track.album.album_name
            result[index]['album']['image_url'] = track.album.cover_url
            result[index]['album']['spotify_url'] = track.album.album_url
        return result

    def top_artists(self):
        result = {}
        top_artists = self.data_frame.groupby('artist_id').size().sort_values(ascending=False)[:self.top_n]
        for index, artist_id in enumerate(top_artists.keys(), 1):
            artist = self.spotify.get_artist(artist_id)
            result[index] = {}
            result[index]['plays'] = int(top_artists[artist_id])
            result[index]['id'] = artist.artist_id
            result[index]['name'] = artist.artist_name
            result[index]['image_url'] = artist.artist_picture_url
            result[index]['spotify_url'] = artist.artist_url
        return result

    def top_albums(self):
        result = {}
        top_albums = self.data_frame.groupby('album_id').size().sort_values(ascending=False)[:self.top_n]
        for index, album_id in enumerate(top_albums.keys(), 1):
            album = self.spotify.get_album(album_id)
            result[index] = {}
            result[index]['plays'] = int(top_albums[album_id])
            result[index]['id'] = album.album_id
            result[index]['name'] = album.album_name
            result[index]['image_url'] = album.cover_url
            result[index]['spotify_url'] = album.album_url
            result[index]['artist'] = {}
            result[index]['artist']['id'] = album.artist.artist_id
            result[index]['artist']['name'] = album.artist.artist_name
            result[index]['artist']['image_url'] = album.artist.artist_picture_url
            result[index]['artist']['spotify_url'] = album.artist.artist_url
        return result

    def _attribute_by_time_unit(self, attribute, day_or_hour_or_dayofweek, count_or_mean):
        result = {}
        time_unit = self.times.dt.__getattribute__(day_or_hour_or_dayofweek)
        grouped = self.data_frame.groupby([time_unit])[attribute]
        data = grouped.__getattribute__(count_or_mean)()
        for unit in data.keys():
            result[int(unit)] = round(data[unit], 2) if count_or_mean == 'mean' else int(data[unit])
        return result

    def bpm_mean(self):
        return round(self.data_frame['track_bpm'].mean(), 2)

    def bpm_by_hour_of_day(self):
        return self._attribute_by_time_unit('track_bpm', 'hour', 'mean')

    def bpm_by_day_of_month(self):
        return self._attribute_by_time_unit('track_bpm', 'day', 'mean')

    def bpm_by_day_of_week(self):
        return self._attribute_by_time_unit('track_bpm', 'dayofweek', 'mean')

    def energy_mean(self):
        return round(self.data_frame['track_energy'].mean(), 2)

    def energy_by_hour_of_day(self):
        return self._attribute_by_time_unit('track_energy', 'hour', 'mean')

    def energy_by_day_of_month(self):
        return self._attribute_by_time_unit('track_energy', 'day', 'mean')

    def energy_by_day_of_week(self):
        return self._attribute_by_time_unit('track_energy', 'dayofweek', 'mean')

    def valence_mean(self):
        return round(self.data_frame['track_valence'].mean(), 2)

    def valence_by_hour_of_day(self):
        return self._attribute_by_time_unit('track_valence', 'hour', 'mean')

    def valence_by_day_of_month(self):
        return self._attribute_by_time_unit('track_valence', 'day', 'mean')

    def valence_by_day_of_week(self):
        return self._attribute_by_time_unit('track_valence', 'dayofweek', 'mean')

    def plays(self):
        return len(self.data_frame)

    def plays_by_hour_of_day(self):
        return self._attribute_by_time_unit('track_id', 'hour', 'count')

    def plays_by_day_of_month(self):
        return self._attribute_by_time_unit('track_id', 'day', 'count')

    def plays_by_day_of_week(self):
        return self._attribute_by_time_unit('track_id', 'dayofweek', 'count')

    def plays_by_month(self):
        return self._attribute_by_time_unit('track_id', 'month', 'count')

    def plays_by_year(self):
        return self._attribute_by_time_unit('track_id', 'year', 'count')

    def as_inner_dict(self):
        return {
            'bpm': {
                'average': self.bpm_mean(),
                'by_day_of_month': self.bpm_by_day_of_month(),
                'by_day_of_week': self.bpm_by_day_of_week(),
                'by_hour': self.bpm_by_hour_of_day(),
            },
            'energy': {
                'average': self.energy_mean(),
                'by_day_of_month': self.energy_by_day_of_month(),
                'by_day_of_week': self.energy_by_day_of_week(),
                'by_hour': self.energy_by_hour_of_day(),
            },
            'plays': {
                'total': self.plays(),
                'by_day_of_month': self.plays_by_day_of_month(),
                'by_day_of_week': self.plays_by_day_of_week(),
                'by_hour': self.plays_by_hour_of_day(),
            },
            'top_list': {
                'top_tracks': self.top_tracks(),
                'top_artists': self.top_artists(),
                'top_albums': self.top_albums(),
            },
            'valence': {
                'average': self.valence_mean(),
                'by_day_of_month': self.valence_by_day_of_month(),
                'by_day_of_week': self.valence_by_day_of_week(),
                'by_hour': self.valence_by_hour_of_day(),
            },
        }


class HoergewohnheitenMonthStats(HoergewohnheitenStatsMixin):

    def __init__(self, year, month):
        self.spotify = SPOTIFY
        self.data_frame = self._load_csv_files(year=year, month=month)
        self.times = self._get_times()
        self.top_n = 50

    def as_dict(self):
        return self.as_inner_dict()


class HoergewohnheitenYearStats(HoergewohnheitenStatsMixin):

    def __init__(self, year):
        self.spotify = SPOTIFY
        self.data_frame = self._load_csv_files(year=year)
        self.times = self._get_times()
        self.top_n = 100

    def as_dict(self):
        inner_dict = self.as_inner_dict()
        inner_dict['plays']['by_month'] = self.plays_by_month()
        return inner_dict


class HoergewohnheitenAllTimeStats(HoergewohnheitenStatsMixin):

    def __init__(self):
        self.spotify = SPOTIFY
        self.data_frame = self._load_csv_files()
        self.times = self._get_times()
        self.top_n = 100

    def as_dict(self):
        inner_dict = self.as_inner_dict()
        inner_dict['plays']['by_year'] = self.plays_by_year()
        inner_dict['plays']['by_month'] = self.plays_by_month()
        return inner_dict
