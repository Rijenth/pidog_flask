from flask import Blueprint, request, jsonify
from utils.image_utils import decode_image_from_base64, save_face_encoding, load_known_faces
# import face_recognition
import requests

face_bp = Blueprint("faces", __name__)

@face_bp.route("/detect-face", methods=["POST"])
def detect_face():
    response = requests.post(
        "http://15.237.33.168:8890/detect-face",
        json = request.json
    )
    return response.json()


@face_bp.route("/add-face", methods=["POST"])
def add_face():
    response = requests.post(
        "http://15.237.33.168:8890/add-face",
        json = request.json
    )
    return response.json()


@face_bp.route("/recognize", methods=["POST"])
def recognize():
    response = requests.post(
        "http://15.237.33.168:8890/recognize",
        json = request.json
    )
    return response.json()