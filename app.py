import base64
import logging
import os

import cv2
import face_recognition
import numpy as np
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Répertoire des visages que l'on considère comme "non intrus"
KNOWN_FACE_DIR = "known_faces"
os.makedirs(KNOWN_FACE_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='dog.log', filemode='a',
                    format='%(asctime)s - %(message)s')

# Configure face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/send-command", methods=["POST"])
def send_command():
    command = request.form.get("command")

    match command:
        case 'start-patrol':
            return 'start patrol function', 200
        case 'stop-patrol':
            return 'stop patrol function', 200
        case 'start-camera':
            return 'start-camera', 200
        case 'stop-camera':
            return 'stop-camera', 200
        case str() if command:
            return f"Commande '{command}' reçue", 200
    
    return "Aucune commande reçue.", 400


@app.route("/detect-face", methods=["POST"])
def detect_face():
    data_url = request.json.get("image")
    if not data_url:
        return jsonify({"error": "No image provided"}), 400

    # Extraire l’image base64
    header, encoded = data_url.split(",", 1)
    img_data = base64.b64decode(encoded)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    return jsonify({
        "faces_detected": len(faces),
        "someone_present": len(faces) > 0
    })

@app.route("/list-faces", methods=["GET"])
def list_faces():
    faces = [f.replace(".npy", "") for f in os.listdir(KNOWN_FACE_DIR) if f.endswith(".npy")]
    return jsonify(faces)

@app.route("/delete-face", methods=["POST"])
def delete_face():
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Nom manquant"}), 400

    file_path = os.path.join(KNOWN_FACE_DIR, f"{name}.npy")
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"status": "deleted", "name": name})
    else:
        return jsonify({"error": "Fichier introuvable"}), 404

def save_face_encoding(name, encoding):
    path = os.path.join(KNOWN_FACE_DIR, f"{name}.npy")
    np.save(path, encoding)

def load_known_faces():
    known_encodings = []
    known_names = []
    for file in os.listdir(KNOWN_FACE_DIR):
        if file.endswith(".npy"):
            encoding = np.load(os.path.join(KNOWN_FACE_DIR, file))
            name = file.replace(".npy", "")
            known_encodings.append(encoding)
            known_names.append(name)
    return known_names, known_encodings

def decode_image_from_base64(data_url):
    header, encoded = data_url.split(",", 1)
    img_data = base64.b64decode(encoded)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

@app.route("/add-face", methods=["POST"])
def add_face():
    data = request.json
    name = data.get("name")
    image_b64 = data.get("image")

    if not name or not image_b64:
        return jsonify({"error": "Missing name or image"}), 400

    image = decode_image_from_base64(image_b64)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        return jsonify({"error": "Aucun visage détecté"}), 400

    save_face_encoding(name, encodings[0])
    return jsonify({"status": "saved", "name": name})

@app.route("/recognize", methods=["POST"])
def recognize():
    image_b64 = request.json.get("image")
    if not image_b64:
        return jsonify({"error": "Image manquante"}), 400

    image = decode_image_from_base64(image_b64)
    input_encodings = face_recognition.face_encodings(image)

    if not input_encodings:
        return jsonify({"status": "no_face"})

    known_names, known_encodings = load_known_faces()

    for input_encoding in input_encodings:
        matches = face_recognition.compare_faces(known_encodings, input_encoding, tolerance=0.5)
        if True in matches:
            name = known_names[matches.index(True)]
            return jsonify({"status": "authorized", "person": name})

    return jsonify({"status": "intruder"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
