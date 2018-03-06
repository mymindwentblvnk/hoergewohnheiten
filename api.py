from datetime import datetime, timedelta

from flask import jsonify
from flask_restful import Resource
from models import db, Play, Track, Album, Artist


def arg_date_to_datetime(from_date, to_date):
    f = datetime.strptime(from_date, '%Y-%m-%d') if from_date else datetime(2017, 8, 1)
    t = datetime.strptime(to_date, '%Y-%m-%d') if to_date else datetime.now()
    t = t + timedelta(days=1)  # To receive the whole day
    return f, t


class Plays(Resource):

    def get(self, user_name):
        latest_plays = Play.query.\
                            filter_by(user_name=user_name).\
                            order_by(Play.played_at_cet.desc()).\
                            limit(20).\
                            all()
        result = []

        for play in latest_plays:
            result.append(play.to_dict())

        response = jsonify({
            'meta': {
                'user_name': user_name,
            },
            'latest_plays': result,
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


class ResourceMixin(object):

    def _apply_meta_data(self, unit, user_name, from_date, to_date, resource):
        return {
            'meta': {
                'from_date': from_date,
                'to_date': to_date,
                'user_name': user_name,
                'unit': unit,
                'resource': resource,
            },
        }


class Counts(Resource, ResourceMixin):

    N = 100

    def _arg_date_to_datetime(self, from_date, to_date):
        f = datetime.strptime(from_date, '%Y-%m-%d') if from_date else datetime(2017, 8, 1)
        t = datetime.strptime(to_date, '%Y-%m-%d') if to_date else datetime.now()
        t = t + timedelta(days=1)  # To receive the whole day
        return f, t

    def _get_count_per_track(self, user_name, from_date, to_date):
        plays_per_track = []
        counts = db.session.\
            query(db.func.count(Play.track_id).label('cnt'), Play.track_id).\
            filter_by(user_name=user_name).\
            filter(Play.played_at_cet >= from_date).\
            filter(Play.played_at_cet <= to_date).\
            group_by(Play.track_id).\
            order_by(db.desc('cnt')).\
            limit(self.N).\
            all()
        for count, track_id in counts:
            track = Track.query.get(track_id)
            plays_per_track.append({'count': count, 'track': track.to_dict()})
        return {'data': plays_per_track}

    def _get_count_per_artist(self, user_name, from_date, to_date):
        plays_per_artist = []
        counts = db.session.\
            query(db.func.count(Artist.artist_id).label('cnt'), Artist.artist_id).\
            select_from(Play).\
            filter_by(user_name=user_name).\
            filter(Play.played_at_cet >= from_date).\
            filter(Play.played_at_cet <= to_date).\
            join(Play.track).\
            join(Track.artists).\
            group_by(Artist.artist_id).\
            order_by(db.desc('cnt')).\
            limit(self.N).\
            all()
        for count, artist_id in counts:
            artist = Artist.query.get(artist_id)
            plays_per_artist.append({'count': count, 'artist': artist.to_dict()})
        return {'data': plays_per_artist}

    def _get_count_per_album(self, user_name, from_date, to_date):
        plays_per_album = []
        counts = db.session.\
            query(db.func.count(Album.album_id).label('cnt'), Album.album_id).\
            select_from(Play).\
            filter_by(user_name=user_name).\
            filter(Play.played_at_cet >= from_date).\
            filter(Play.played_at_cet <= to_date).\
            join(Play.track).\
            join(Track.album).\
            group_by(Album.album_id).\
            order_by(db.desc('cnt')).\
            limit(self.N).\
            all()
        for count, album_id in counts:
            album = Album.query.get(album_id)
            plays_per_album.append({'count': count, 'album': album.to_dict()})
        return {'data': plays_per_album}

    def _get_count_per_day(self, user_name, from_date, to_date):
        plays_per_day = dict()
        counts = db.session.\
            query(db.func.count(Play.day_of_week).label('cnt'), Play.day_of_week).\
            filter_by(user_name=user_name).\
            filter(Play.played_at_cet >= from_date).\
            filter(Play.played_at_cet <= to_date).\
            group_by(Play.day_of_week).\
            order_by(db.asc(Play.day_of_week)).\
            limit(self.N).\
            all()
        for count, day in counts:
            plays_per_day[day] = count
        return {'data': plays_per_day}

    def _get_count_per_hour(self, user_name, from_date, to_date):
        plays_per_hour = dict()
        counts = db.session.\
            query(db.func.count(Play.hour).label('cnt'), Play.hour).\
            filter_by(user_name=user_name).\
            filter(Play.played_at_cet >= from_date).\
            filter(Play.played_at_cet <= to_date).\
            group_by(Play.hour).\
            order_by(db.asc(Play.hour)).\
            limit(self.N).\
            all()
        for count, hour in counts:
            plays_per_hour[hour] = count
        return {'data': plays_per_hour}

    def _get_count_per_month(self, user_name, from_date, to_date):
        plays_per_month = dict()
        counts = db.session.\
            query(db.func.count(Play.month).label('cnt'), Play.month).\
            filter_by(user_name=user_name).\
            filter(Play.played_at_cet >= from_date).\
            filter(Play.played_at_cet <= to_date).\
            group_by(Play.month).\
            order_by(db.asc(Play.month)).\
            limit(self.N).\
            all()
        for count, month in counts:
            plays_per_month[month] = count
        return {'data': plays_per_month}

    def _get_data_by_unit(self, unit, user_name, from_date, to_date):

        UNIT_MAPPING = {
            'artist': self._get_count_per_artist,
            'track': self._get_count_per_track,
            'album': self._get_count_per_album,
            'hour': self._get_count_per_hour,
            'day': self._get_count_per_day,
            'month': self._get_count_per_month,
        }
        if unit in UNIT_MAPPING:
            return UNIT_MAPPING[unit](user_name, from_date, to_date)
        return {}

    def get(self, unit, user_name, from_date=None, to_date=None):
        from_date, to_date = arg_date_to_datetime(from_date, to_date)
        data = self._get_data_by_unit(unit, user_name, from_date, to_date)
        data.update(self._apply_meta_data(unit, user_name, from_date, to_date, resource='count'))
        response = jsonify(data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


class AudioFeature(Resource, ResourceMixin):

    def _get_audio_feature_per_month(self, user_name, from_date, to_date):
        sql = """SELECT
    avg((t_track.audio_feature_data->>'tempo') :: FLOAT) AS avg_tempo,
    avg((t_track.audio_feature_data->>'energy') :: FLOAT) AS avg_energy,
    avg((t_track.audio_feature_data->>'valence') :: FLOAT) AS avg_valence,
    avg((t_track.audio_feature_data->>'key') :: FLOAT) AS avg_key,
    avg((t_track.audio_feature_data->>'loudness') :: FLOAT) AS avg_loudness,
    t_play.month
FROM
    t_play
JOIN t_track ON t_play.track_id = t_track.track_id
WHERE t_play.user_name = '{}'
AND t_play.played_at_cet >= '{}-{}-{}'
AND t_play.played_at_cet <= '{}-{}-{}'
GROUP BY t_play.month
ORDER BY t_play.month ASC"""

        rows = db.session.execute(sql.format(user_name,
                                  from_date.year,
                                  from_date.month,
                                  from_date.day,
                                  to_date.year,
                                  to_date.month,
                                  to_date.day))
        return self._rows_to_data(rows)

    def _get_audio_feature_per_day(self, user_name, from_date, to_date):
        sql = """SELECT
    avg((t_track.audio_feature_data->>'tempo') :: FLOAT) AS avg_tempo,
    avg((t_track.audio_feature_data->>'energy') :: FLOAT) AS avg_energy,
    avg((t_track.audio_feature_data->>'valence') :: FLOAT) AS avg_valence,
    avg((t_track.audio_feature_data->>'key') :: FLOAT) AS avg_key,
    avg((t_track.audio_feature_data->>'loudness') :: FLOAT) AS avg_loudness,
    t_play.day_of_week
FROM
    t_play
JOIN t_track ON t_play.track_id = t_track.track_id
WHERE t_play.user_name = '{}'
AND t_play.played_at_cet >= '{}-{}-{}'
AND t_play.played_at_cet <= '{}-{}-{}'
GROUP BY t_play.day_of_week
ORDER BY t_play.day_of_week ASC"""

        rows = db.session.execute(sql.format(user_name,
                                  from_date.year,
                                  from_date.month,
                                  from_date.day,
                                  to_date.year,
                                  to_date.month,
                                  to_date.day))
        return self._rows_to_data(rows)

    def _get_audio_feature_per_hour(self, user_name, from_date, to_date):
        sql = """SELECT
    avg((t_track.audio_feature_data->>'tempo') :: FLOAT) AS avg_tempo,
    avg((t_track.audio_feature_data->>'energy') :: FLOAT) AS avg_energy,
    avg((t_track.audio_feature_data->>'valence') :: FLOAT) AS avg_valence,
    avg((t_track.audio_feature_data->>'key') :: FLOAT) AS avg_key,
    avg((t_track.audio_feature_data->>'loudness') :: FLOAT) AS avg_loudness,
    t_play.hour
FROM
    t_play
JOIN t_track ON t_play.track_id = t_track.track_id
WHERE t_play.user_name = '{}'
AND t_play.played_at_cet >= '{}-{}-{}'
AND t_play.played_at_cet <= '{}-{}-{}'
GROUP BY t_play.hour
ORDER BY t_play.hour ASC"""

        rows = db.session.execute(sql.format(user_name,
                                  from_date.year,
                                  from_date.month,
                                  from_date.day,
                                  to_date.year,
                                  to_date.month,
                                  to_date.day))
        return self._rows_to_data(rows)

    def _rows_to_data(self, rows):
        result = dict()
        for row in rows:
            result[str(row[5])] = {
                'avg_tempo': row[0],
                'avg_energy': row[1],
                'avg_valence': row[2],
                'avg_key': row[3],
                'avg_loudness': row[4]
            }
        return {'data': result}

    def _get_data_by_unit(self, unit, user_name, from_date, to_date):

        UNIT_MAPPING = {
            'hour': self._get_audio_feature_per_hour,
            'day': self._get_audio_feature_per_day,
            'month': self._get_audio_feature_per_month,
        }
        if unit in UNIT_MAPPING:
            return UNIT_MAPPING[unit](user_name, from_date, to_date)
        return {}

    def get(self, unit, user_name, from_date=None, to_date=None):
        from_date, to_date = arg_date_to_datetime(from_date, to_date)
        data = self._get_data_by_unit(unit, user_name, from_date, to_date)
        data.update(self._apply_meta_data(unit, user_name, from_date, to_date, resource='audio_feature'))
        response = jsonify(data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
