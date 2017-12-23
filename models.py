from datetime import datetime

from sqlalchemy import Column, DateTime, String, BigInteger, Integer, Float, ForeignKey, func, asc
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import settings


Base = declarative_base()


class Track(Base):

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
