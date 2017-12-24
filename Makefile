VENV_NAME=venv

${VENV_NAME}:
	@echo "Creating environment."
	virtualenv -p python3 ${VENV_NAME}; . ${VENV_NAME}/bin/activate; pip install -r requirements.txt; deactivate

init-db:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Running main.py.";
	. ${VENV_NAME}/bin/activate; python init_db.py; deactivate

run:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Running main.py.";
	. ${VENV_NAME}/bin/activate; python main.py ${ARGS}; deactivate

flake8:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Checking for PEP 8.";
	. ${VENV_NAME}/bin/activate; flake8 . --exclude ${VENV_NAME}; deactivate
