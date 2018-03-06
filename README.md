# Hoergewohnheiten

The Python script `extract_spotify_plays.py` uses the Spotify Web API (with the help of [plamere's spotipy](https://github.com/plamere/spotipy)) to extract your recent Spotify plays and loads it to a PostgreSQL database. With `app.py` there is a Flask application serving stats about your listing behaviour via a REST API.

## Flask API Endpoints

### Plays
```GET /plays/user/<user_name>```
#### Result
Returns a list of the latest played tracks.
```
{
  "latest_plays": [
    {
      "played_at_cet": "Mon, 05 Mar 2018 20:52:24 GMT", 
      "track": {
        "album": {
          "artists": [
            {
              "id": "00sazWvoTLOqg5MFwC68Um", 
              "image_url": "https://i.scdn.co/image/51f6ae7cf53c70291f2f07c154b9ae2193239111", 
              "name": "Yann Tiersen", 
              "spotify_url": "https://open.spotify.com/artist/00sazWvoTLOqg5MFwC68Um"
            }
          ], 
          "id": "6BpM86nsNY2MdlAa33Msq9", 
          "image_url": "https://i.scdn.co/image/6d6cc5253216f476aaaea505c12ea3d074d79f9c", 
          "name": "Die fabelhafte Welt der Amelie (Das Original-H\u00f6rspiel zum Film)", 
          "spotify_url": "https://open.spotify.com/album/6BpM86nsNY2MdlAa33Msq9"
        }, 
        "artists": [
          {
            "id": "00sazWvoTLOqg5MFwC68Um", 
            "image_url": "https://i.scdn.co/image/51f6ae7cf53c70291f2f07c154b9ae2193239111", 
            "name": "Yann Tiersen", 
            "spotify_url": "https://open.spotify.com/artist/00sazWvoTLOqg5MFwC68Um"
          }, 
          {
            "id": "7EV6jW6dotBdvsHj6xPixi", 
            "image_url": "https://i.scdn.co/image/43d53b2a4385d466b460913901b83f41177a05f8", 
            "name": "The Divine Comedy", 
            "spotify_url": "https://open.spotify.com/artist/7EV6jW6dotBdvsHj6xPixi"
          }
        ], 
        "audio_feature": {
          "energy": 0.339, 
          "key": 7, 
          "loudness": -8.123, 
          "tempo": 100.104, 
          "valence": 0.952
        }, 
        "duration": 183466, 
        "id": "7GrXQbXokarlsCjozXmqvC", 
        "name": "Les jours tristes - Instrumental", 
        "spotify_url": "https://open.spotify.com/track/7GrXQbXokarlsCjozXmqvC"
      }
    }, 
    {
      "played_at_cet": "Mon, 05 Mar 2018 20:49:04 GMT", 
      "track": {
        "album": {
          "artists": [
            {
              "id": "7EV6jW6dotBdvsHj6xPixi", 
              "image_url": "https://i.scdn.co/image/43d53b2a4385d466b460913901b83f41177a05f8", 
              "name": "The Divine Comedy", 
              "spotify_url": "https://open.spotify.com/artist/7EV6jW6dotBdvsHj6xPixi"
            }
          ], 
          "id": "4pFkI7o1FTl2wWon60zrog", 
          "image_url": "https://i.scdn.co/image/39d9ddd6d00eee9d71acc3bd250f567a01c62c36", 
          "name": "Bang Goes The Knighthood", 
          "spotify_url": "https://open.spotify.com/album/4pFkI7o1FTl2wWon60zrog"
        }, 
        "artists": [
          {
            "id": "7EV6jW6dotBdvsHj6xPixi", 
            "image_url": "https://i.scdn.co/image/43d53b2a4385d466b460913901b83f41177a05f8", 
            "name": "The Divine Comedy", 
            "spotify_url": "https://open.spotify.com/artist/7EV6jW6dotBdvsHj6xPixi"
          }
        ], 
        "audio_feature": {
          "energy": 0.57, 
          "key": 6, 
          "loudness": -9.873, 
          "tempo": 116.016, 
          "valence": 0.962
        }, 
        "duration": 198306, 
        "id": "5CmQgmKwmSf3ojZTuvHekY", 
        "name": "At The Indie Disco", 
        "spotify_url": "https://open.spotify.com/track/5CmQgmKwmSf3ojZTuvHekY"
      }
    }, 
    ...
  ], 
  "meta": {
    "user_name": "<user_name>"
  }
}

```

### Count of Plays
```GET /counts/per/<unit>/user/<user_name>/from/2018-01-01/to/2018-03-01```

`<unit>` can be 
* `track`
* `album`
* `artist`
* `hour`
* `day`
* `month`

```/from/2018-01-01/to/2018-03-01``` can be left out (or only the to date)

#### Result per Track (per Album/Artists is similar to that)
Returns a sorted list of the most played tracks with their play count.
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

#### Result per Track (per Album/Artists is similar to that)
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

### Audio Features
```GET /audiofeatures/per/<unit>/user/<user_name>/from/2018-01-01/to/2018-03-01```

`<unit>` can be 
* `hour`
* `day`
* `month`

```/from/2018-01-01/to/2018-03-01``` can be left out (or only the to date)

#### Result per Day (per Hour/Month is similar to that)
Returns a object with average audio feature data per day of week.
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
      ...
    }, 
    "3": {
        ...
    }, 
    "4": {
      ...
    }, 
    "5": {
      ...
    }, 
    "6": {
      ...
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
