VENV_NAME='venv'

env:
	@echo "Creating environment."
	virtualenv -p python3 ${VENV_NAME}; . ${VENV_NAME}/bin/activate; pip install -r requirements.txt; deactivate

run:
	if [ ! -d ${VENV_NAME} ]; then @echo "Environment not found."; make env; fi
	@echo "Running main.py.";
	. ${VENV_NAME}/bin/activate; python main.py; deactivate 
