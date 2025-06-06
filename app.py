from flask import Flask, render_template, request, Response
from routes.face_routes import face_bp
from routes.command_routes import command_bp
from robot import close_dog, PIDOG_AVAILABLE  # appel indirect à pidog
import os
import logging
import cv2
import base64

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

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError("Impossible d'ouvrir la caméra. Essaye un autre index (0 ou 1).")

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode l'image en JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Stream en MJPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/capture-image', methods=['GET'])
def capture_image():
    success, frame = camera.read()
    if not success:
        return {'error': 'Erreur de capture'}, 500
    # Encode en JPEG puis en base64
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return {'image': 'data:image/jpeg;base64,' + img_base64}

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8888)
    except KeyboardInterrupt:
        pass
    finally:
        if PIDOG_AVAILABLE:
            close_dog()