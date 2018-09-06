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
	. ${VENV_NAME}/bin/activate; python extract/main.py ${ARGS}; deactivate

flake8:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Checking for PEP 8.";
	. ${VENV_NAME}/bin/activate; flake8 . --config=./flake8.config; deactivate

docker-build:
	make docker-clean
	sudo docker build -t hoergewohnheiten-image --no-cache=true .

docker-clean:
	-sudo docker rm -f hoergewohnhiten-container
	-sudo docker rmi hoergewohnheiten-image

docker-run-extraction:
	sudo docker run --rm -a stdout -a stderr --name hoergewohnheiten-container -v $(shell pwd):/workdir -i hoergewohnheiten-image /bin/bash -c "python extract/main.py"
	

docker-create-database-tables:
	sudo docker run --rm -a stdout -a stderr --name hoergewohnheiten-container -v $(shell pwd):/workdir -i gun-image /bin/bash -c 'python -c "from models import PostgreSQLConnection; PostgreSQLConnection().create_db()"'
