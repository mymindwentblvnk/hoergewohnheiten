# Hoergewohnheiten

The Python script `extract_spotify_plays.py` uses the Spotify Web API (with the help of [plamere's spotipy](https://github.com/plamere/spotipy)) to extract your recent Spotify plays and loads it to a PostgreSQL database. With `app.py` there is a Flask application serving stats about your listing behaviour via a REST API.

## Flask API Endpoints

tbd.

## Control Flow
```
 +--------------------------------------+
 |                                      |
 | Spotify Web API                      |
 | (v1/me/player/recently-played)       |
 |                                      |
 +---------------------+----------------+
                       |
 +---------------------|----------------+
 |                     |                |
 | Hoergewohnheiten    |                |
 |                     v                |
 | +-------------------+--------------+ |   +-----------------------+
 | |                                  | |   |                       |
 | | [Batch] extract_spotify_plays.py +---->+ [Database] PostgreSQL |
 | |                                  | |   |                       |
 | +----------------------------------+ |   |                       |
 |                                      |   |                       |
 | +----------------------------------+ |   |                       |
 | |                                  | |   |                       |
 | | [REST API] app.py                +<----+                       |
 | | [Flask]                          | |   |                       |
 | |                                  | |   |                       |
 | +-------------------+--------------+ |   +-----------------------+
 |                     |                |
 +---------------------|----------------+
                       |
                       v
 +---------------------+----------------+
 |                                      |
 | [App] Reading JSON                   |
 |       Showing beautiful stats        |
 |                                      |
 +--------------------------------------+
```

## Entity–Relationship Model
```
            +------------------------------------------+
            | t_play                                   |
            +------------------------------------------+
            | created_at_utc: DateTime                 |
            | played_at_utc_timestamp: BigInteger [PK] |
            | played_at_utc: DateTime                  |
            | played_at_cet: DateTime                  |
            | day: Integer                             |
            | month: Integer                           |
            | year: Integer                            |
            | hour: Integer                            |
            | minute: Integer                          |
            | second: Integer                          |
            | day_of_week: Integer                     |
            | week_of_year: Integer                    |
            | track_id: String                         |
            | user_name: String                        |
            +-----+------------------------------------+
                  |
                  |
                  | n..1
                  |
                  |
+-----------------+--------+         +--------------------------+
| t_track                  |         | t_album                  |
+--------------------------+         +--------------------------+
| created_at_utc: DateTime |   n..1  | created_at_utc: DateTime |
| track_id: String [PK]    +---------+ album_id: String [PK]    |
| album_id: String         |         | album_data: JSON         |
| track_data: JSON         |         +-----+--------------------+
| audio_feature_data: JSON |               |
+----------------------+---+               |
                       |                   |
                       |                   |
                       | 1..n              | 1..n
                       |                   |
                       |                   |
         +-------------+---+        +------+----------+
         | t_track_artists |        | t_album_artists |
         +-----------------+        +-----------------+
         | track_id        |        | album_id        |
         | artist_id       |        | artist_id       |
         +-------------+---+        +------+----------+
                       |                   |
                       |                   |
                       | n..1              | n..1
                       |                   |
                       |                   |
                    +--+-------------------+---+
                    | t_artist                 |
                    +--------------------------+
                    | created_at_utc: DateTime |
                    | artist_id: String [PK]   |
                    | artist_data: JSON        |
                    +--------------------------+

 ```
