# Hoergewohnheiten

The Python script `extract_spotify_plays.py` uses the Spotify Web API (with the help of [plamere's spotipy](https://github.com/plamere/spotipy)) to extract your recent Spotify plays and loads it to a PostgreSQL database. With `app.py` there is a Flask application serving stats about your listing behaviour via a REST API.

## Flask API Endpoints

### Plays
```GET /plays/user/<user_name>```

### Count of Plays (per Track/Album/Artist)
#### Per Track
```GET /counts/per/track/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result
```
{
  "meta": {
    "from_date": "Tue, 01 Aug 2017 00:00:00 GMT", 
    "resource": "count", 
    "to_date": "Wed, 07 Mar 2018 08:37:41 GMT", 
    "unit": "track", 
    "user_name": "<user_name>"
  },
  "data": [
    {
      "count": 97, 
      "track": {
        "duration": 755855, 
        "id": "0lQRATnAHfiULVw36bIpDJ", 
        "name": "computiful", 
        "spotify_url": "https://open.spotify.com/track/0lQRATnAHfiULVw36bIpDJ"
        "album": {
          "artists": [
            {
              "id": "3utZ2yeQk0Z3BCOBWP7Vlu", 
              "image_url": "https://i.scdn.co/image/01f1c5b433c462150aa033c912e55e688719fb3c", 
              "name": "Cro", 
              "spotify_url": "https://open.spotify.com/artist/3utZ2yeQk0Z3BCOBWP7Vlu"
            }
          ], 
          "id": "4E7RXXUaKpkquRTcVUvdAg", 
          "image_url": "https://i.scdn.co/image/0a6633c93c8eef4aa815305ad6d688c6cf8e3ac1", 
          "name": "tru. (Deluxe Edition)", 
          "spotify_url": "https://open.spotify.com/album/4E7RXXUaKpkquRTcVUvdAg"
        }, 
        "artists": [
          {
            "id": "3utZ2yeQk0Z3BCOBWP7Vlu", 
            "image_url": "https://i.scdn.co/image/01f1c5b433c462150aa033c912e55e688719fb3c", 
            "name": "Cro", 
            "spotify_url": "https://open.spotify.com/artist/3utZ2yeQk0Z3BCOBWP7Vlu"
          }
        ], 
        "audio_feature": {
          "energy": 0.401, 
          "key": 9, 
          "loudness": -11.685, 
          "tempo": 89.96, 
          "valence": 0.378
        },
      }
    },
    ...
  ]
}
```

#### Per Album
```GET /counts/per/album/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result
As above.

#### Per Artist
```GET /counts/per/artist/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result
As above.

### Count of Plays (per Hour/Day/Month)
#### Per Hour
```GET /counts/per/hour/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result
```
{
  "data": {
    "0": 742, 
    "1": 406, 
    "2": 255, 
    "3": 94, 
    "4": 34, 
    "5": 40, 
    "6": 43, 
    "7": 123, 
    "8": 320, 
    "9": 651, 
    "10": 696, 
    "11": 898, 
    "12": 885, 
    "13": 936, 
    "14": 1070, 
    "15": 1111, 
    "16": 1271, 
    "17": 1069, 
    "18": 1223, 
    "19": 1197, 
    "20": 1199, 
    "21": 1273, 
    "22": 1109, 
    "23": 843
  }, 
  "meta": {
    "from_date": "Tue, 01 Aug 2017 00:00:00 GMT", 
    "resource": "count", 
    "to_date": "Wed, 07 Mar 2018 08:49:07 GMT", 
    "unit": "hour", 
    "user_name": "<user_name>"
  }
}
```
#### Per Day
```GET /counts/per/day/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result
As above.

#### Per Month
```GET /counts/per/month/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result
As above.

### Audio Features (per Hour/Day/Month)
#### Per Day
```GET /audiofeatures/per/day/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result
```
{
  "data": {
    "0": {
      "avg_energy": 0.551325090768637, 
      "avg_key": 5.24642719196601, 
      "avg_loudness": -10.2777879490151, 
      "avg_tempo": 118.715380455775, 
      "avg_valence": 0.40613955195056
    }, 
    "1": {
      "avg_energy": 0.539121522828284, 
      "avg_key": 5.29252525252525, 
      "avg_loudness": -10.5345975757576, 
      "avg_tempo": 116.41779030303, 
      "avg_valence": 0.38840694949495
    }, 
    "2": {
      "avg_energy": 0.566855514579761, 
      "avg_key": 5.27958833619211, 
      "avg_loudness": -9.98453945111494, 
      "avg_tempo": 116.93982890223, 
      "avg_valence": 0.411569468267581
    }, 
    "3": {
      "avg_energy": 0.560633994407158, 
      "avg_key": 5.27404921700224, 
      "avg_loudness": -10.2001771066369, 
      "avg_tempo": 116.792395227442, 
      "avg_valence": 0.420372632363908
    }, 
    "4": {
      "avg_energy": 0.530835986930414, 
      "avg_key": 5.09961144471918, 
      "avg_loudness": -10.5677513246202, 
      "avg_tempo": 115.044523489933, 
      "avg_valence": 0.408663087248321
    }, 
    "5": {
      "avg_energy": 0.537262560762102, 
      "avg_key": 5.29093717816684, 
      "avg_loudness": -10.0944526261586, 
      "avg_tempo": 116.890798661174, 
      "avg_valence": 0.447021627188465
    }, 
    "6": {
      "avg_energy": 0.524706814084507, 
      "avg_key": 5.41327967806841, 
      "avg_loudness": -10.85093722334, 
      "avg_tempo": 115.591962173039, 
      "avg_valence": 0.403796458752515
    }
  }, 
  "meta": {
    "from_date": "Tue, 01 Aug 2017 00:00:00 GMT", 
    "resource": "audio_feature", 
    "to_date": "Wed, 07 Mar 2018 08:55:25 GMT", 
    "unit": "day", 
    "user_name": "<user_name>"
  }
}
```
#### Per Hour
```GET /audiofeatures/per/hour/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result 
As above.

#### Per Month
```GET /audiofeatures/per/month/user/<user_name>/from/2018-01-01/to/2018-03-01```
#### Result 
As above.


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
