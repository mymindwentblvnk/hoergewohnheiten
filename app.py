import os
from datetime import datetime

from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

import settings


app = Flask(__name__)


# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[settings.POSTGRES_ENVIRON_KEY]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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
            'artists': self.track_artists,
            'album': self.album,
        }

    @property
    def track_name(self):
        return self.track_data['name']

    @property
    def spotify_url(self):
        return self.track_data['external_urls']['spotify'],

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

    @property
    def track_artists(self):
        result = []
        for artist in self.track_data['artists']:
            result.append(
                {
                    'id': artist['id'],
                    'name': artist['name'],
                    'spotify_url': artist['external_urls']['spotify'],
                }
            )
        return result

    @property
    def album(self):
        return {
            'name': self.album_data['name'],
            'id': self.album_data['id'],
            'spotify_url': self.album_data['external_urls']['spotify'],
        }


class Track(db.Model, TrackMixin):

    # Meta
    __tablename__ = 't_track'
    created_at_utc = db.Column(db.DateTime, default=datetime.utcnow)

    # Payload
    track_id = db.Column(db.String, primary_key=True, index=True)
    track_data = db.Column(db.JSON, nullable=False)
    album_data = db.Column(db.JSON, nullable=False)
    audio_feature_data = db.Column(db.JSON)

    # Relationships
    plays = db.relationship('Play', back_populates='track')



class PlayMixin(object):

    def to_dict(self):
        return {
            'played_at_cet': self.played_at_cet,
            'track': self.track.to_dict(),
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

    def get(self, user_name, from_date, to_date):
        response = jsonify({
            'from_date': from_date,
            'to_date': to_date,
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


class Plays(Resource):

    def get(self, user_name, offset=None):
        latest_plays = Play.query.\
                            filter_by(user_name=user_name).\
                            order_by(Play.played_at_cet.desc()).\
                            limit(20).\
                            all()
        result = []

        for play in latest_plays:
            result.append(play.to_dict())

        response = jsonify({
            'offset': offset,
            'latest_plays': result,
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


api.add_resource(Plays, '/plays/<string:user_name>',
                        '/plays/<string:user_name>/<int:offset>')
api.add_resource(Stats, '/stats/<string:user_name>',
                        '/stats/<string:user_name>/<string:from_date>',
                        '/stats/<string:user_name>/<string:from_date>/<string:to_date>')


if __name__ == '__main__':
    app.run(debug=True)
