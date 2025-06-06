from flask import Blueprint, request, jsonify
from utils.image_utils import decode_image_from_base64, save_face_encoding, load_known_faces
import face_recognition

face_bp = Blueprint("faces", __name__)

@face_bp.route("/detect-face", methods=["POST"])
def detect_face():
    data_url = request.json.get("image")
    if not data_url:
        return jsonify({"error": "No image provided"}), 400

    image = decode_image_from_base64(data_url)
    face_locations = face_recognition.face_locations(image, model='hog')
    return jsonify({
        "faces_detected": len(face_locations),
        "someone_present": len(face_locations) > 0
    })


@face_bp.route("/add-face", methods=["POST"])
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


@face_bp.route("/recognize", methods=["POST"])
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