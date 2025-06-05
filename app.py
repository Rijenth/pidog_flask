from flask import Flask, render_template, request
#from routes.face_routes import face_bp
#from routes.command_routes import command_bp
import os
import logging
import cv2

from pidog import Pidog
from preset_actions import pant
from preset_actions import body_twisting
from time import sleep

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
#app.register_blueprint(face_bp)
#app.register_blueprint(command_bp)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# Robot -> 
my_dog = Pidog(head_init_angles=[0, 0, -30])
sleep(1)

def wake_up():
    # stretch
    my_dog.rgb_strip.set_mode('listen', color='yellow', bps=0.6, brightness=0.8)
    my_dog.do_action('stretch', speed=50)
    my_dog.head_move([[0, 0, 30]]*2, immediately=True)
    my_dog.wait_all_done()
    sleep(0.2)
    body_twisting(my_dog)
    my_dog.wait_all_done()
    sleep(0.5)
    my_dog.head_move([[0, 0, -30]], immediately=True, speed=90)
    # sit and wag_tail
    my_dog.do_action('sit', speed=25)
    my_dog.wait_legs_done()
    my_dog.do_action('wag_tail', step_count=10, speed=100)
    my_dog.rgb_strip.set_mode('breath', color=[245, 10, 10], bps=2.5, brightness=0.8)
    pant(my_dog, pitch_comp=-30, volume=80)
    my_dog.wait_all_done()
    # hold
    my_dog.do_action('wag_tail', step_count=10, speed=30)
    my_dog.rgb_strip.set_mode('breath', 'pink', bps=0.5)
    while True:
        sleep(1)

@app.route("/send-command", methods=["POST"])
def send_command():
    command = request.form.get("command")
    match command:
        case 'start-patrol':
            wake_up()
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)