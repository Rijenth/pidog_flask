from flask import Blueprint, request
from robot import awake_dog, start_patrol, stop_patrol, sleep_dog  # appel indirect à pidog

command_bp = Blueprint("commands", __name__)

@command_bp.route("/send-command", methods=["POST"])
def send_command():
    command = request.form.get("command")

    match command:
        case 'awake-dog':
            awake_dog()
            return 'awake-dog', 200
        
        case 'sleep-dog':
            sleep_dog()
            return 'sleep-dog', 200

        case 'start-patrol':
            start_patrol()
            return 'start patrol function', 200

        case 'stop-patrol':
            stop_patrol()
            return 'stop patrol function', 200

        case 'start-camera':
            return 'start-camera', 200

        case 'stop-camera':
            return 'stop-camera', 200

        case str() if command:
            return f"Commande '{command}' reçue", 200

    return "Aucune commande reçue.", 400