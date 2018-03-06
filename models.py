from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


track_artists = db.Table('t_track_artists',
                         db.Column('track_id', db.String, db.ForeignKey('t_track.track_id')),
                         db.Column('artist_id', db.String, db.ForeignKey('t_artist.artist_id')))


album_artists = db.Table('t_album_artists',
                         db.Column('album_id', db.String, db.ForeignKey('t_album.album_id')),
                         db.Column('artist_id', db.String, db.ForeignKey('t_artist.artist_id')))


class Artist(db.Model):

    # Meta
    __tablename__ = 't_artist'
    created_at_utc = db.Column(db.DateTime, default=datetime.utcnow)

    # Payload
    artist_id = db.Column(db.String, primary_key=True, index=True)
    artist_data = db.Column(db.JSON, nullable=False)

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

    def to_dict(self):
        return {
            'id': self.artist_id,
            'name': self.artist_name,
            'spotify_url': self.spotify_url,
            'image_url': self.image_url,
        }



class Album(db.Model):

    # Meta
    __tablename__ = 't_album'
    created_at_utc = db.Column(db.DateTime, default=datetime.utcnow)

    # Payload
    album_id = db.Column(db.String, primary_key=True, index=True)
    album_data = db.Column(db.JSON, nullable=False)

    # Relationships
    artists = db.relationship('Artist', secondary=album_artists)
    tracks = db.relationship('Track')

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

    def to_dict(self):
        return {
            'id': self.album_id,
            'name': self.album_name,
            'spotify_url': self.spotify_url,
            'artists': [a.to_dict() for a in self.artists],
            'image_url': self.image_url,
        }


class Track(db.Model):

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

    @property
    def duration(self):
        return self.track_data['duration_ms']

    @property
    def track_name(self):
        return self.track_data['name']

    @property
    def spotify_url(self):
        return self.track_data['external_urls']['spotify']

    @property
    def key(self):
        if self.audio_feature_data:
            return self.audio_feature_data['key']

    @property
    def loudness(self):
        if self.audio_feature_data:
            return self.audio_feature_data['loudness']

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

    def to_dict(self):
        return {
            'id': self.track_id,
            'name': self.track_name,
            'spotify_url': self.spotify_url,
            'duration': self.duration,
            'audio_feature': {
                'tempo': self.tempo,
                'valence': self.valence,
                'energy': self.energy,
                'key': self.key,
                'loudness': self.loudness,
            },
            'artists': [a.to_dict() for a in self.artists],
            'album': self.album.to_dict(),
        }


class Play(db.Model):

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

    def to_dict(self):
        return {
            'track': self.track.to_dict(),
            'played_at_cet': self.played_at_cet,
        }
