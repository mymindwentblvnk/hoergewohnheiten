import os
from datetime import datetime, timedelta

from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

import settings


app = Flask(__name__)


# SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if settings.POSTGRES_ENVIRON_KEY in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[settings.POSTGRES_ENVIRON_KEY]
else:
    import secret_settings
    app.config['SQLALCHEMY_DATABASE_URI'] = secret_settings.POSTGRES_CONNECTION_STRING
db = SQLAlchemy(app)


track_artists = db.Table('t_track_artists',
                         db.Column('track_id', db.String, db.ForeignKey('t_track.track_id')),
                         db.Column('artist_id', db.String, db.ForeignKey('t_artist.artist_id')))


album_artists = db.Table('t_album_artists',
                         db.Column('album_id', db.String, db.ForeignKey('t_album.album_id')),
                         db.Column('artist_id', db.String, db.ForeignKey('t_artist.artist_id')))


class ArtistMixin(object):

    def to_dict(self):
        return {
            'id': self.artist_id,
            'name': self.artist_name,
            'spotify_url': self.spotify_url,
            'image_url': self.image_url,
        }

    @property
    def image_url(self):
        last_width = 0
        url = None
        for image in self.artist_data['images']:
            if last_width < image['width']:
                last_width = image['width']
                url = image['url']
        return url

    @property
    def artist_name(self):
        return self.artist_data['name']

    @property
    def spotify_url(self):
        return self.artist_data['external_urls']['spotify']


class Artist(db.Model, ArtistMixin):

    # Meta
    __tablename__ = 't_artist'
    created_at_utc = db.Column(db.DateTime, default=datetime.utcnow)

    # Payload
    artist_id = db.Column(db.String, primary_key=True, index=True)
    artist_data = db.Column(db.JSON, nullable=False)


class AlbumMixin(object):

    def to_dict(self):
        return {
            'id': self.album_id,
            'name': self.album_name,
            'spotify_url': self.spotify_url,
            'artists': [a.to_dict() for a in self.artists],
            'image_url': self.image_url,
        }

    @property
    def image_url(self):
        last_width = 0
        url = None
        for image in self.album_data['images']:
            if last_width < image['width']:
                last_width = image['width']
                url = image['url']
        return url

    @property
    def spotify_url(self):
        return self.album_data['external_urls']['spotify']

    @property
    def album_name(self):
        return self.album_data['name']


class Album(db.Model, AlbumMixin):

    # Meta
    __tablename__ = 't_album'
    created_at_utc = db.Column(db.DateTime, default=datetime.utcnow)

    # Payload
    album_id = db.Column(db.String, primary_key=True, index=True)
    album_data = db.Column(db.JSON, nullable=False)

    # Relationships
    artists = db.relationship('Artist', secondary=album_artists)
    tracks = db.relationship('Track')


class TrackMixin(object):

    def to_dict(self):
        return {
            'id': self.track_id,
            'name': self.track_name,
            'spotify_url': self.spotify_url,
            'audio_feature': {
                'tempo': self.tempo,
                'valence': self.valence,
                'energy': self.energy,
            },
            'artists': [a.to_dict() for a in self.artists],
            'album': self.album.to_dict(),
        }

    @property
    def track_name(self):
        return self.track_data['name']

    @property
    def spotify_url(self):
        return self.track_data['external_urls']['spotify']

    @property
    def tempo(self):
        if self.audio_feature_data:
            return self.audio_feature_data['tempo']

    @property
    def energy(self):
        if self.audio_feature_data:
            return self.audio_feature_data['energy']

    @property
    def valence(self):
        if self.audio_feature_data:
            return self.audio_feature_data['valence']


class Track(db.Model, TrackMixin):

    # Meta
    __tablename__ = 't_track'
    created_at_utc = db.Column(db.DateTime, default=datetime.utcnow)

    # Payload
    track_id = db.Column(db.String, primary_key=True, index=True)
    track_data = db.Column(db.JSON, nullable=False)
    album_id = db.Column(db.String, db.ForeignKey('t_album.album_id'), index=True)
    audio_feature_data = db.Column(db.JSON)

    # Relationships
    plays = db.relationship('Play', back_populates='track')
    album = db.relationship('Album', back_populates='tracks')
    artists = db.relationship('Artist', secondary=track_artists)


class PlayMixin(object):

    def to_dict(self):
        return {
            'track': self.track.to_dict(),
            'played_at_cet': self.played_at_cet,
        }


class Play(db.Model, PlayMixin):

    __tablename__ = 't_play'
    created_at_utc = db.Column(db.DateTime, default=datetime.utcnow)

    # Payload
    played_at_utc_timestamp = db.Column(db.BigInteger, primary_key=True)
    played_at_utc = db.Column(db.DateTime, nullable=False)
    played_at_cet = db.Column(db.DateTime, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    second = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # Monday: 0, Sunday: 6
    week_of_year = db.Column(db.Integer, nullable=False)
    track_id = db.Column(db.String, db.ForeignKey('t_track.track_id'), index=True)
    user_name = db.Column(db.String, nullable=False)

    # Relationship
    track = db.relationship('Track', back_populates='plays')


# RESTful
api = Api(app)


class Stats(Resource):

    N = 100

    def get_plays_per_album(self, user_name, from_date, to_date):
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
            plays_per_album.append({'count': count, 'album': album.to_dict(), })

        return plays_per_album

    def get_plays_per_artist(self, user_name, from_date, to_date):
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
            plays_per_artist.append({'count': count, 'artist': artist.to_dict(), })

        return plays_per_artist


    def get_plays_per_track(self, user_name, from_date, to_date):
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
            plays_per_track.append({'count': count, 'track': track.to_dict(), })

        return plays_per_track

    def get_total_plays(self, user_name, from_date, to_date):
        return Play.query.\
            filter_by(user_name=user_name).\
            filter(Play.played_at_cet >= from_date).\
            filter(Play.played_at_cet <= to_date).\
            count()

    def get_plays_per_day_of_week(self, user_name, from_date, to_date):
        plays_per_day_of_week = []
        counts = db.session.\
            query(db.func.count(Play.day_of_week).label('cnt'), Play.day_of_week).\
            filter_by(user_name=user_name).\
            filter(Play.played_at_cet >= from_date).\
            filter(Play.played_at_cet <= to_date).\
            group_by(Play.day_of_week).\
            order_by(db.asc(Play.day_of_week)).\
            limit(self.N).\
            all()

        for count, day_of_week in counts:
            plays_per_day_of_week.append({day_of_week: count, })

        return plays_per_day_of_week

    def get_plays_per_hour_of_day(self, user_name, from_date, to_date):
        plays_per_hour_of_day = []
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
            plays_per_hour_of_day.append({hour: count, })

        return plays_per_hour_of_day

    def get_plays_per_month(self, user_name, from_date, to_date):
        plays_per_month = []
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
            plays_per_month.append({month: count, })

        return plays_per_month

    def get_audio_feature_per_month(self, user_name, from_date, to_date):
        result = dict()
        sql = """SELECT
    avg((t_track.audio_feature_data->>'tempo') :: FLOAT) AS avg_tempo,
    avg((t_track.audio_feature_data->>'energy') :: FLOAT) AS avg_energy,
    avg((t_track.audio_feature_data->>'valence') :: FLOAT) AS avg_valence,
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
        for row in rows:
            result[str(row[3])] = {
                'avg_tempo': row[0],
                'avg_energy': row[1],
                'avg_valence': row[2]
            }
        return result

    def get_audio_feature_per_day_of_week(self, user_name, from_date, to_date):
        result = dict()
        sql = """SELECT
    avg((t_track.audio_feature_data->>'tempo') :: FLOAT) AS avg_tempo,
    avg((t_track.audio_feature_data->>'energy') :: FLOAT) AS avg_energy,
    avg((t_track.audio_feature_data->>'valence') :: FLOAT) AS avg_valence,
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
        for row in rows:
            result[str(row[3])] = {
                'avg_tempo': row[0],
                'avg_energy': row[1],
                'avg_valence': row[2]
            }
        return result

    def get_audio_feature_per_hour(self, user_name, from_date, to_date):
        result = dict()
        sql = """SELECT
    avg((t_track.audio_feature_data->>'tempo') :: FLOAT) AS avg_tempo,
    avg((t_track.audio_feature_data->>'energy') :: FLOAT) AS avg_energy,
    avg((t_track.audio_feature_data->>'valence') :: FLOAT) AS avg_valence,
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
        for row in rows:
            result[str(row[3])] = {
                'avg_tempo': row[0],
                'avg_energy': row[1],
                'avg_valence': row[2]
            }
        return result

    def _arg_date_to_datetime(self, from_date, to_date):
        f = datetime.strptime(from_date, '%Y-%m-%d') if from_date else datetime(2017, 8, 1)
        t = datetime.strptime(to_date, '%Y-%m-%d') if to_date else datetime.now()
        t = t + timedelta(days=1)  # To receive the whole day
        return f, t

    def get(self, user_name, from_date=None, to_date=None):
        from_date, to_date = self._arg_date_to_datetime(from_date, to_date)

        response = jsonify({
            'meta': {
                'from_date': from_date,
                'to_date': to_date,
                'user_name': user_name,
            },
            'plays': {
                'per_track': self.get_plays_per_track(user_name, from_date, to_date),
                'per_album': self.get_plays_per_album(user_name, from_date, to_date),
                'per_artist': self.get_plays_per_artist(user_name, from_date, to_date),
                'total': self.get_total_plays(user_name, from_date, to_date),
                'per_day_of_week': self.get_plays_per_day_of_week(user_name, from_date, to_date),
                'per_hour_of_day': self.get_plays_per_hour_of_day(user_name, from_date, to_date),
                'per_month': self.get_plays_per_month(user_name, from_date, to_date),
            },
            'audio_feature': {
                'per_month': self.get_audio_feature_per_month(user_name, from_date, to_date),
                'per_hour': self.get_audio_feature_per_hour(user_name, from_date, to_date),
                'per_day_of_week': self.get_audio_feature_per_day_of_week(user_name, from_date, to_date),
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


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


api.add_resource(Plays, '/plays/<string:user_name>')
api.add_resource(Stats, '/stats/<string:user_name>',
                        '/stats/<string:user_name>/<string:from_date>',
                        '/stats/<string:user_name>/<string:from_date>/<string:to_date>')


if __name__ == '__main__':
    app.run(debug=True)
