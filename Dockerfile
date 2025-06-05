FROM python:3.11-slim

ENV APP_HOME=/app
WORKDIR $APP_HOME

# Installer les dépendances système
RUN apt-get clean && apt-get -y update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    git \
    cmake \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers requis et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV USE_PIDOG=false

CMD ["flask", "run", "--host=0.0.0.0", "--port=8888", "--debug"]
