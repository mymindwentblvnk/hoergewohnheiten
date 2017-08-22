# Hoergewohnheiten

This Python script uses the Spotify Web API (with the help of [plamere's spotipy](https://github.com/plamere/spotipy)) to receive your recent Spotify plays. The data is loaded to a CSV file and will automaticly be uploaded to a GitHub repository. To enhance data the scripts collects 

* bpm, energy and valence of the played track (taken from [Audio Features](https://developer.spotify.com/web-api/get-audio-features/) of the Web API)
* genre of the artist (taken from [Artist](https://developer.spotify.com/web-api/get-artist/) of the Web API)
* label and genre of the album (both taken from [Album](https://developer.spotify.com/web-api/get-album/) of the Web API)
* weather data (temperature and weather status) from Open Weather Map ("What music do I like when it is raining?")

## What The Data Looks Like

You can see my data repository here [HoergewohnheitenData](https://github.com/michael-123/HoergewohnheitenData). The data looks like this:

| played_at_as_utc | track_id | track_name | track_bpm | track_energy | track_valence | artist_id | artist_name | artist_genres | album_id | album_name | album_label | album_genres | weather_temperature | weather_status |
|------------------|----------|------------|-----------|--------------|-----------|-------------|----------|------------|-------------|--------------|---------------------|----------------|--|--|
| 2017-08-10 16:57:51.210000|4tSLFGKiSO4O1d5aXJUpGJ|Doomsday|95.409|0.84|0.812|2pAWfrd7WFF3XhVt9GooDL|MF DOOM|alternative hip hop, chillhop, east coast hip hop, escape room, hardcore hip hop, hip hop, rap, underground hip hop|0h8L3oHRHSCF2lDDbGnpm1|Operation Doomsday: Original Version Remastered|Metal Face Records||20.58|haze |
| 2017-08-10 17:57:44.705000|4o0FNtV322Ixj9dqallluS|Bugatti|129.961|0.561|0.261|0aZu9zUfF2EgTHyBbZlW1C|LGoony|deep german hip hop, underground hip hop|2O1eye3JacqELubyVNzxfQ|Intergalactica|Airforce Luna||20.58|haze |
| 2017-08-11 11:54:33.055000|0p6O4QpOWXrSnbzYKRDy4L|Lieblingsmensch|88.012|0.351|0.556|2Q570lQPWiuP2dCOP69jO3|Remoe|deep german hip hop|2kh8DovYXyL7o3uJmuX6IT|Alles für die Fam|Alles für die Fam Records||20.58|haze |
| 2017-08-11 12:24:27.248000|4r7iDEGdW2Gw9hJlCbi5qL|Mi Negrita|117.954|0.4|0.579|1YZEoYFXx4AxVv13OiOPvZ|Devendra Banhart|chamber pop, folk christmas, folk-pop, freak folk, indie christmas, indie folk, indie pop, indie rock, indietronica, new weird america|1Z69PSnbIBojgF9NBJbKca|Mala|Nonesuch||20.58|haze |
| 2017-08-14 08:53:47.297000|7ol59kVwq3DQyyjKZ2DRzy|Jungle|146.002|0.697|0.489|6zVFRTB0Y1whWyH7ZNmywf|Tash Sultana|deep australian indie|5fPbbwEgH8qX4uIrmPchYi|Notion|Lonely Lands Records||20.58|haze |
| 2017-08-18 07:25:42.455000|3B54sVLJ402zGa6Xm4YGNe|Unforgettable|97.985|0.769|0.75|6vXTefBL93Dj5IqAWq6OTv|French Montana|dwn trap, pop rap, rap, trap music|4c2p3TdN7NcQfCXyueCNnC|Jungle Rules|Bad Boy Entertainment/Epic Records||20.58|haze |


## What Questions Can Be Answered With This Data

The idea is to answer questions like

* My favorite tracks/artists/albums per day/week/year/ever
* My favorite music label 
* My favorite genre per day/week/year/ever
* What music do I like the most if it is cloudy outside?
* What music is best for me when the sun is shining?
* What energy must a song have to fit my morning routine?
* If enough data is collected I can generate a playlist every morning based on the weather.

## What Is Needed?

* Spotify API information ([Spotify Developer Console](https://developer.spotify.com/my-applications/#!/applications))
* Open Weather Map API key and the ID of your hometown
* A second GitHub repository for storing the CSV files (must be cloned via SSH so the script can upload the updates without entering credentials)
