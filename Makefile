.PHONY: setup run clean

# Crée l'environnement virtuel et installe les dépendances
setup:
	python3 -m venv venv
	source venv/bin/activate && pip install -r requirements.txt

# Active l'environnement et lance le serveur Flask
run:
	source venv/bin/activate && FLASK_APP=app.py flask run --host=0.0.0.0

# Supprime l'environnement virtuel (clean project)
clean:
	rm -rf venv