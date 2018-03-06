VENV_NAME=venv

${VENV_NAME}:
	@echo "Creating environment."
	virtualenv -p python3 ${VENV_NAME}; . ${VENV_NAME}/bin/activate; pip install -r requirements.txt; deactivate

create-database:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Create database.";
	. ${VENV_NAME}/bin/activate; python -c "from models import PostgreSQLConnection; PostgreSQLConnection().create_db()"; deactivate

run-server:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Starting server.";
	. ${VENV_NAME}/bin/activate; python app.py; deactivate

run:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Extracting spotify plays.";
	. ${VENV_NAME}/bin/activate; python extract_spotify_plays/main.py ${ARGS}; deactivate

flake8:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Checking for PEP 8.";
	. ${VENV_NAME}/bin/activate; flake8 . --config=./flake8.config; deactivate
