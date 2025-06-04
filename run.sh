#!/bin/bash

# Active l'environnement virtuel s'il existe, sinon le crée avec Python 3.11
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with Python 3.11..."
    python3.11 -m venv venv
fi
source venv/bin/activate

# Installe les dépendances si besoin
pip install -r requirements.txt

# Démarre l'application Flask
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8888 --debug