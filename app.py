from flask import Flask, request, render_template
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='dog.log', filemode='a',
                    format='%(asctime)s - %(message)s')

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/send-command", methods=["POST"])
def send_command():
    command = request.form.get("command")
    if command:
        logging.info(f"Donnée reçue : {command}")
        return f"Commande '{command}' reçue et enregistrée dzadaz."
    return "Aucune commande reçue.", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)