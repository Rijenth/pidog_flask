#!/bin/bash

# Active l'environnement virtuel s'il existe, sinon le crée
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

# Installe Flask si besoin
pip install -r requirements.txt

# Démarre l'application Flask
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8888