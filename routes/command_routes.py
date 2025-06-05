from flask import Blueprint, request

command_bp = Blueprint("commands", __name__)

@command_bp.route("/send-command", methods=["POST"])
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