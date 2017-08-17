# Hoergewohnheiten

This Python script uses the Spotify Web API (with the help of [plamere's spotipy](https://github.com/plamere/spotipy)) to receive your recent Spotify plays. The data is loaded to a CSV file and will automaticly be uploaded to a GitHub repository. To enhance data the scripts collects 

* weather data from Open Weather Map ("What music do I like when it is raining?")
* bpm and the energy of the played track (both taken from [Audio Features](https://developer.spotify.com/web-api/get-audio-features/) of the Web API)
* label and genre of the album (both taken from [Album](https://developer.spotify.com/web-api/get-album/) endpoint of the Web API)

## What The Data Looks Like

You can see my data repository here [HoergewohnheitenData](https://github.com/michael-123/HoergewohnheitenData). The data looks like this:

| played_at | track_id | track_name | track_bpm | track_energy | artist_id | artist_name | album_id | album_name | album_label | album_genres | weather_temperature | weather_status |
|-----------|----------|------------|-----------|--------------|-----------|-------------|----------|------------|-------------|--------------|---------------------|----------------|
| 2017-08-17 12:17:50.782000 | 0HqXBQtXt6quSgZDKkoflI | freisein | 120.077 | 0.78 | 73JMQvllbBsfDclpXOW4Wj | morten | 3tOvdq705xY714EgYcfuJi | freisein | Morten | | 25.0 | broken clouds |
| 2017-08-17 12:18:30.297000 | 46F8PBRZTHR1IYuhKKuNl2 | Turn Off The Lights (Whos Afraid Of The Dark) - Original Mix | 123.998 | 0.892 | 7nqpEU6DCHkNtK1bYsyS3W | Kerri Chandler | 78Ob8dIG0FxLtVeZc6EYo6 | Turn Off The Lights (Whos Afraid Of The Dark) Remixes | Kaoz Theory | | 25.39 | broken clouds |
| 2017-08-17 12:22:28.532000 | 16nWs4O6mbYl7K1KzriegE | Timeflys | 160.003 | 0.644| 1pYqeD9g56MUo0Oatod3eN | DJ Mastercard | 4HawD6YDlxaGzdFBjPqCvC | Corrupt Memories | Mall Music Inc. | | 25.39 | broken clouds |
| 2017-08-17 12:25:18.445000 | 7FdQfxvybWVBu5EGCNmyA5 | Lethal | 159.97 | 0.909 | 1pYqeD9g56MUo0Oatod3eN | DJ Mastercard | 4HawD6YDlxaGzdFBjPqCvC | Corrupt Memories| Mall Music Inc. | | 25.39 | broken clouds |
| 2017-08-17 12:29:09.414000 | 7BUVpPIzqKisolRNQJ0mug | In the Dark | 160.018 | 0.74 | 1pYqeD9g56MUo0Oatod3eN | DJ Mastercard | 4HawD6YDlxaGzdFBjPqCvC | Corrupt Memories| Mall Music Inc. | | 25.39 | broken clouds |
| 2017-08-17 12:30:27.159000 | 3RJgpnQdw7pGt88OLxjOyA | Always | 159.953 | 0.677 | 1pYqeD9g56MUo0Oatod3eN | DJ Mastercard | 4HawD6YDlxaGzdFBjPqCvC | Corrupt Memories| Mall Music Inc. | | 25.39 | broken clouds |
| 2017-08-17 12:34:09.047000 | 3Bym3y1VjgCmDxQx6hC5AX | All I Do | 160.951 | 0.525 | 1pYqeD9g56MUo0Oatod3eN | DJ Mastercard| 4HawD6YDlxaGzdFBjPqCvC | Corrupt Memories | Mall Music Inc. | | 25.39 | broken clouds |
| 2017-08-17 12:54:28.433000 | 6cL7NCFSvqWrBH5r4mkvVV | Superman | 194.902 | 0.935| 7sVQKNtdP2NylxMgbNOJMM | Goldfinger | 2Fhk8LPPX8d14HwEKjmJ1O | The Best Of Goldfinger | Jive | | 25.4 | broken clouds|

## What Questions Can Be Answered With This Data

The idea is to answer questions like

* My favorite tracks/artists/albums per day/week/year/ever
* My favorite music label 
* My favorite genre per day/week/year/ever
* What music do I like the most if it is cloudy outside?
* What music is best for me is best for me when the sun is shining?
* What energy must a song have to fit the weather?
* If enough data is collected I can generate a playlist every morning based on the weather.

## What Is Needed?

* Spotify API information ([Spotify Developer Console](https://developer.spotify.com/my-applications/#!/applications))
* Open Weather Map API key and the ID of your hometown
* A second GitHub repository for storing the CSV files (must be cloned via SSH so the script can upload the updates without entering credentials)
