from flask import Flask, render_template
from routes.face_routes import face_bp
from routes.command_routes import command_bp
import os
import logging
import cv2

app = Flask(__name__)

# Répertoire des visages connus
KNOWN_FACE_DIR = "known_faces"
os.makedirs(KNOWN_FACE_DIR, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO, filename='dog.log', filemode='a',
                    format='%(asctime)s - %(message)s')

# Cascade pour détection (potentiellement utile)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Routes
app.register_blueprint(face_bp)
app.register_blueprint(command_bp)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)