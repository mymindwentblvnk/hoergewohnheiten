# Requests For Pull Requests

* Refactoring of app.py (grows to be a monolith)
  
  * Removing flask_sqlalchemy models from app.py
  * Remove flask_restful resources from app.py

* Unify models: SQLAlchemy models appear in models.py (for extraction script) and app.py (for flask app)

* Introduce tests with native PostgreSQL database

* Enable Travis CI

* Installation tutorials
  
  * How to run spotipy (auth flow)
  * How to install the flask application at e. g. Heroku
