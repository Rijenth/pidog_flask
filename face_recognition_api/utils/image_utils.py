import base64
import numpy as np
import cv2
import os

KNOWN_FACE_DIR = "known_faces"

def decode_image_from_base64(data_url):
    header, encoded = data_url.split(",", 1)
    img_data = base64.b64decode(encoded)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

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