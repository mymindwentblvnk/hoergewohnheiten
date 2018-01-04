# Hoergewohnheiten

This Python script uses the Spotify Web API (with the help of [plamere's spotipy](https://github.com/plamere/spotipy)) to extract your recent Spotify plays and loads it to a PostgreSQL database.

## What The Data Looks Like
```
 ------------------------------------------
| t_play                                   |
 ------------------------------------------
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
 ------------------------------------------

 --------------------------
| t_track                  |
 --------------------------
| created_at_utc: DateTime |
| track_id: String [PK]    |
| album_id: String         |
| track_data: JSON         |
| audio_feature_data: JSON |
 --------------------------

 --------------------------
| t_album                  |
 --------------------------
| created_at_utc: DateTime |
| album_id: String [PK]    |
| album_data: JSON         |
 --------------------------

 --------------------------
| t_artist                 |
 --------------------------
| created_at_utc: DateTime |
| artist_id: String [PK]   |
| artist_data: JSON        |
 --------------------------

 -----------------
| t_album_artists |
 -----------------
| album_id        |
| artist_id       |
 -----------------

 -----------------
| t_track_artists |
 -----------------
| track_id        |
| artist_id       |
 -----------------
 ```

Relationships:

* `t_play --- Many-To-One --- t_track`
* `t_track --- Many-To-One --- t_album`
* `t_track --- One-To-Many --- t_track_artists --- Many-To-One --- t_artist`
* `t_album --- One-To-Many --- t_album_artists --- Many-To-One --- t_artist`
