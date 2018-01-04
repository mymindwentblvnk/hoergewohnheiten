# Hoergewohnheiten

This Python script uses the Spotify Web API (with the help of [plamere's spotipy](https://github.com/plamere/spotipy)) to extract your recent Spotify plays and loads it to a PostgreSQL database.

## Entity–relationship model
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
                  |                                                                                                                                       
                  |                                                                                                                                       
                  | n..1                                                                                                                                  
                  |                                                                                                                                       
                  |                                                                                                                                       
 --------------------------           --------------------------                                                                                          
| t_track                  |         | t_album                  |                                                                                         
 --------------------------           --------------------------                                                                                          
| created_at_utc: DateTime |   n..1  | created_at_utc: DateTime |                                                                                         
| track_id: String [PK]    |---------| album_id: String [PK]    |                                                                                         
| album_id: String         |         | album_data: JSON         |                                                                                         
| track_data: JSON         |          --------------------------                                                                                          
| audio_feature_data: JSON |               |                                                                                                              
 --------------------------                |                                                                                                              
                       |                   |                                                                                                              
                       |                   |                                                                                                              
                       | 1..n              | 1..n                                                                                                         
                       |                   |                                                                                                              
                       |                   |                                                                                                              
          -----------------          -----------------                                                                                                    
         | t_album_artists |        | t_track_artists |                                                                                                   
          -----------------          -----------------                                                                                                    
         | album_id        |        | track_id        |                                                                                                   
         | artist_id       |        | artist_id       |                                                                                                   
          -----------------          -----------------                                                                                                    
                       |                   |                                                                                                              
                       |                   |                                                                                                              
                       | n..1              | n..1                                                                                                         
                       |                   |                                                                                                              
                       |                   |                                                                                                              
                     --------------------------                                                                                                            
                    | t_artist                 |                                                                                                          
                     --------------------------                                                                                                            
                    | created_at_utc: DateTime |                                                                                                          
                    | artist_id: String [PK]   |                                                                                                          
                    | artist_data: JSON        |                                                                                                          
                     --------------------------   
 ```
