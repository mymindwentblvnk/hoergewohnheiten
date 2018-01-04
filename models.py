from datetime import datetime
import os

from sqlalchemy import Column, DateTime, String, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import settings


Base = declarative_base()


track_artists = Table('t_track_artists',
                      Base.metadata,
                      Column('track_id', String, ForeignKey('t_track.track_id')),
                      Column('artist_id', String, ForeignKey('t_artist.artist_id')))


album_artists = Table('t_album_artists',
                      Base.metadata,
                      Column('album_id', String, ForeignKey('t_album.album_id')),
                      Column('artist_id', String, ForeignKey('t_artist.artist_id')))


class Artist(Base):

    # Meta
    __tablename__ = 't_artist'
    created_at_utc = Column(DateTime, default=datetime.utcnow)

    # Payload
    artist_id = Column(String, primary_key=True)
    artist_data = Column(JSON, nullable=False)


class Album(Base):

    # Meta
    __tablename__ = 't_album'
    created_at_utc = Column(DateTime, default=datetime.utcnow)

    # Payload
    album_id = Column(String, primary_key=True)
    album_data = Column(JSON, nullable=False)

    # Relationship
    artists = relationship('Artist', secondary=album_artists)
    tracks = relationship('Track')


class Track(Base):

    # Meta
    __tablename__ = 't_track'
    created_at_utc = Column(DateTime, default=datetime.utcnow)

    # Payload
    track_id = Column(String, primary_key=True, index=True)
    album_id = Column(String, ForeignKey('t_album.album_id'), index=True)
    track_data = Column(JSON, nullable=False)
    audio_feature_data = Column(JSON)

    # Relationships
    plays = relationship('Play', back_populates='track')
    album = relationship('Album', back_populates='tracks')
    artists = relationship('Artist', secondary=track_artists)


class Play(Base):

    # Meta
    __tablename__ = 't_play'
    created_at_utc = Column(DateTime, default=datetime.utcnow)

    # Payload
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


class PostgreSQLConnection(object):

    def __init__(self):
        if settings.POSTGRES_ENVIRON_KEY in os.environ:
            self.engine = create_engine(os.environ[settings.POSTGRES_ENVIRON_KEY])
        else:
            import secret_settings
            self.engine = create_engine(secret_settings.POSTGRES_CONNECTION_STRING)
        self.session = sessionmaker(autoflush=False)(bind=self.engine)

    def drop_db(self):
        Base.metadata.drop_all(bind=self.engine)

    def create_db(self):
        Base.metadata.create_all(bind=self.engine)

    def save_instance(self, instance):
        try:
            self.session.add(instance)
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
        except InvalidRequestError as e:
            self.session.rollback()

    def save_play(self, play):
        try:
            self.session.add(play)
            self.session.commit()
            print("* Track \"{}\" (played at {}) saved.".format(play.track.track_data['name'], play.played_at_cet))
        except IntegrityError as e:
            self.session.rollback()
        except InvalidRequestError as e:
            self.session.rollback()
