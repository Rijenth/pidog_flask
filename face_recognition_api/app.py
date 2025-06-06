from flask import Flask
from routes.face_routes import face_bp

app = Flask(__name__)

# Routes
app.register_blueprint(face_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8890)
