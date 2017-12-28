from sqlalchemy import Column, DateTime, String, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import settings


Base = declarative_base()


class Album(object):

    def __init__(self, album_data):
        self.data = album_data

    @property
    def id(self):
        return self.data['id']

    @property
    def name(self):
        return self.data['name']


class Artist(object):

    def __init__(self, artist_data):
        self.data = artist_data

    @property
    def id(self):
        return self.data['id']

    @property
    def name(self):
        return self.data['name']


class TrackDataAccessMixin(object):

    @property
    def name(self):
        return self.track_data['name']

    @property
    def track_id(self):
        return self.track_data['id']

    @property
    def spotify_url(self):
        return None

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
    def artists(self):
        return None

    @property
    def album(self):
        return None


class Track(Base, TrackDataAccessMixin):

    __tablename__ = 't_track'
    track_id = Column(String, primary_key=True, index=True)
    track_data = Column(JSON, nullable=False)
    album_data = Column(JSON, nullable=False)
    audio_feature_data = Column(JSON)

    # Relationships
    plays = relationship('Play', back_populates='track')


class Play(Base):

    __tablename__ = 't_play'
    played_at_utc_timestamp = Column(BigInteger, primary_key=True)
    played_at_utc = Column(DateTime, nullable=False)
    played_at_cet = Column(DateTime, nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    minute = Column(Integer, nullable=False)
    second = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # Monday: 0, Sunday: 6
    week_of_year = Column(Integer, nullable=False)
    track_id = Column(String, ForeignKey('t_track.track_id'), index=True)
    user_name = Column(String, nullable=False)

    # Relationship
    track = relationship('Track', back_populates='plays')

    @property
    def csv_string(self):
        return "{},{},{}".format(self.played_at_utc_timestamp,
                                 self.track_id,
                                 self.user_name)


class PostgreSQLConnection(object):

    def __init__(self):
        self.engine = create_engine('postgres://{}:{}@{}:{}/{}'.format(settings.POSTGRES_CONNECTION_INFORMATION['user'],
                                                                       settings.POSTGRES_CONNECTION_INFORMATION['password'],
                                                                       settings.POSTGRES_CONNECTION_INFORMATION['host'],
                                                                       settings.POSTGRES_CONNECTION_INFORMATION['port'],
                                                                       settings.POSTGRES_CONNECTION_INFORMATION['database']))
        self.session = sessionmaker(autoflush=False)(bind=self.engine)

    def drop_db(self):
        Base.metadata.drop_all(bind=self.engine)

    def create_db(self):
        Base.metadata.create_all(bind=self.engine)

    def save_play(self, play):
        try:
            self.session.add(play)
            self.session.commit()
            print("* Track \"{}\" saved.".format(play.track.name))
        except IntegrityError as e:
            self.session.rollback()
        except InvalidRequestError as e:
            self.session.rollback()
