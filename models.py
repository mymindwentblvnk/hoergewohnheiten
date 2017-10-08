from sqlalchemy import Column, DateTime, String, Integer, Float, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table, Index, Sequence


Base = declarative_base()
Session = sessionmaker()


class ColumnMixin(object):

    imported_at = Column(DateTime, default=func.now())


class AudioFeature(Base, ColumnMixin):

    __tablename__ = 't_audio_feature'
    track_id = Column(String, ForeignKey('t_track.track_id'), primary_key=True, index=True)
    track = relationship('Track', back_populates='audio_feature')
    tempo = Column(Float)
    valence = Column(Float)
    energy = Column(Float)


album_artists = Table('t_album_artists',
                      Base.metadata,
                      Column('album_id', String, ForeignKey('t_album.album_id')),
                      Column('artist_id', String, ForeignKey('t_artist.artist_id')))


class Album(Base, ColumnMixin):

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


class Artist(Base, ColumnMixin):

    __tablename__ = 't_artist'
    artist_id = Column(String, primary_key=True, index=True)
    artist_name = Column(String)
    spotify_url = Column(String)
    image_url = Column(String)


class Track(Base, ColumnMixin):

    __tablename__ = 't_track'
    track_id = Column(String, primary_key=True, index=True)
    track_name = Column(String)
    spotify_url = Column(String)
    image_url = Column(String)
    # Play (1:n)
    play = relationship('Play')
    # Audio Feature (1:1)
    audio_feature = relationship('AudioFeature', uselist=False, back_populates='track')
    # Album (n:1)
    album_id = Column(String, ForeignKey('t_album.album_id'))
    album = relationship('Album', back_populates='tracks')
    # Artists (n:m)
    artists = relationship('Artist', secondary=track_artists)


class Play(Base, ColumnMixin):

    __tablename__ = 't_play'
    id = Column(Integer, Sequence('play_id_sequence'), primary_key=True)
    played_at_utc = Column(DateTime)
    # Track (n:1)
    track_id = Column(String, ForeignKey('t_track.track_id'), index=True)
    track = relationship('Track', back_populates='play')


class SQLiteConnection(object):

    def __init__(self, db_path):
        self.engine = create_engine('sqlite:///{}'.format(db_path))
        self.session = Session(bind=self.engine)

    def create_db(self):
        Base.metadata.create_all(bind=self.engine)

    def save_model(self, model):
        session.add(model)
