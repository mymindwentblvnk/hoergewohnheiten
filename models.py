from datetime import datetime

from sqlalchemy import Column, DateTime, String, BigInteger, Integer, Float, ForeignKey, func, asc
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import settings


Base = declarative_base()


class Artist(Base):

    __tablename__ = 't_artist'
    artist_id = Column(String, primary_key=True, index=True)
    artist_name = Column(String)
    spotify_url = Column(String)
    image_url = Column(String)


album_artists = Table('t_album_artists',
                      Base.metadata,
                      Column('album_id', String, ForeignKey('t_album.album_id')),
                      Column('artist_id', String, ForeignKey('t_artist.artist_id')))


class Album(Base):

    __tablename__ = 't_album'
    album_id = Column(String, primary_key=True, index=True)
    album_name = Column(String)
    spotify_url = Column(String)
    image_url = Column(String)
    # Tracks (1:n)
    tracks = relationship('Track')
    # Artists (n:m)
    artists = relationship('Artist', secondary=album_artists)


track_artists = Table('t_track_artists',
                      Base.metadata,
                      Column('track_id', String, ForeignKey('t_track.track_id')),
                      Column('artist_id', String, ForeignKey('t_artist.artist_id')))


class Track(Base):

    __tablename__ = 't_track'
    track_id = Column(String, primary_key=True, index=True)
    track_name = Column(String)
    spotify_url = Column(String)
    tempo = Column(Float)
    energy = Column(Float)
    valence = Column(Float)
    album_id = Column(String, ForeignKey('t_album.album_id'))

    # Relationships
    plays = relationship('Play', back_populates='track')
    album = relationship('Album', back_populates='tracks')
    artists = relationship('Artist', secondary=track_artists)


class Play(Base):

    __tablename__ = 't_play'
    played_at_utc_timestamp = Column(BigInteger, primary_key=True)
    played_at_utc = Column(DateTime)
    played_at_cet = Column(DateTime)
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    hour = Column(Integer)
    minute = Column(Integer)
    second = Column(Integer)
    day_of_week = Column(Integer)  # Monday: 0, Sunday: 6
    week_of_year = Column(Integer)
    track_id = Column(String, ForeignKey('t_track.track_id'), index=True)
    user_name = Column(String)

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

    def save_instance(self, instance):
        try:
            self.session.add(instance)
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
        except InvalidRequestError as e:
            self.session.rollback()

    def save_instances(self, instances):
        for instance in instances:
            self.save_instance(instance)


class SQLiteConnection(object):

    def __init__(self, db_path):
        self.db_path = db_path
        self.engine = create_engine('sqlite:///{}'.format(self.db_path))
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

    def save_instances(self, instances):
        for instance in instances:
            self.save_instance(instance)

    @property
    def rows_count_play(self):
        return self.session.query(Play).count()
