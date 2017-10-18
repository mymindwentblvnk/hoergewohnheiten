from sqlalchemy import Column, DateTime, String, Integer, Float, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table, Index, Sequence


Base = declarative_base()


class AudioFeature(Base):

    __tablename__ = 't_audio_feature'
    track_id = Column(String, ForeignKey('t_track.track_id'), primary_key=True, index=True)
    tempo = Column(Float)
    energy = Column(Float)
    valence = Column(Float)
    # Relationships
    track = relationship('Track', back_populates='audio_feature')


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


class Artist(Base):

    __tablename__ = 't_artist'
    artist_id = Column(String, primary_key=True, index=True)
    artist_name = Column(String)
    spotify_url = Column(String)
    image_url = Column(String)


class Track(Base):

    __tablename__ = 't_track'
    track_id = Column(String, primary_key=True, index=True)
    track_name = Column(String)
    spotify_url = Column(String)
    album_id = Column(String, ForeignKey('t_album.album_id'))

    # Relationships
    plays = relationship('Play', back_populates='track')
    album = relationship('Album', back_populates='tracks')
    artists = relationship('Artist', secondary=track_artists)
    audio_feature = relationship('AudioFeature', back_populates='track', uselist=False)


class Play(Base):

    __tablename__ = 't_play'
    id = Column(Integer, Sequence('play_id_sequence'), primary_key=True)
    played_at_utc = Column(DateTime)
    played_at_cet = Column(DateTime)
    track_id = Column(String, ForeignKey('t_track.track_id'), index=True)

    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    hour = Column(Integer)
    minute = Column(Integer)
    second = Column(Integer)

    day_of_week = Column(Integer)  # Monday: 0, Sunday: 6
    week_of_year = Column(Integer)

    # Relationship
    track = relationship('Track', back_populates='plays')


class SQLiteConnection(object):

    def __init__(self, db_path):
        self.engine = create_engine('sqlite:///{}'.format(db_path))
        self.session = sessionmaker()(bind=self.engine)
        # self.drop_db()
        # self.create_db()

    def drop_db(self):
        print("Dropping DB.")
        Base.metadata.drop_all(bind=self.engine)

    def create_db(self):
        print("Creating DB.")
        Base.metadata.create_all(bind=self.engine)

    def save_instance(self, instance):
        self.session.add(instance)
        self.session.commit()

    def save_instances(self, instances):
        for instance in instances:
            print("Saving", instance)
            self.save_instance(instance)
