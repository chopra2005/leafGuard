from __future__ import annotations

import json
import os
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory, session, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from config import CLASS_NAMES, SYMPTOM_MAP, TREATMENT_MAP
from db.logger import PredictionLogger
from inference.model_service import PlantDiseaseModelService
from preprocessing.pipeline import LeafPreprocessor

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
MODEL_PATH = BASE_DIR / "models" / "plant_disease_efficientnetb0.keras"

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

preprocessor = LeafPreprocessor()
prediction_logger = PredictionLogger(BASE_DIR / "predictions.db")

model_service = None
if MODEL_PATH.exists():
    class_names_path = BASE_DIR / "models" / "class_names.json"
    class_names = CLASS_NAMES
    if class_names_path.exists():
        class_names = json.loads(class_names_path.read_text(encoding="utf-8"))
    model_service = PlantDiseaseModelService(MODEL_PATH, class_names, TREATMENT_MAP)


def _is_allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = prediction_logger.get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            error = "Username and password are required"
        else:
            password_hash = generate_password_hash(password)
            if prediction_logger.create_user(username, password_hash):
                user = prediction_logger.get_user_by_username(username)
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("index"))
            else:
                error = "Username already exists"
    return render_template("signup.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    predictions = prediction_logger.get_all_predictions(session["user_id"])
    stats = prediction_logger.get_stats(session["user_id"])
    return render_template("dashboard.html", predictions=predictions, stats=stats)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    file = request.files.get("leaf_image")
    if not file or file.filename == "":
        return jsonify({"error": "Please upload a leaf image file."}), 400

    if not _is_allowed(file.filename):
        return jsonify({"error": "Only JPG, JPEG, and PNG files are supported."}), 400

    if model_service is None:
        return jsonify({"error": "Model file not found at models/plant_disease_efficientnetb0.keras."}), 500

    filename = secure_filename(file.filename)
    image_path = UPLOAD_DIR / filename
    file.save(image_path)

    preprocessed = preprocessor.preprocess_from_path(image_path)
    result = model_service.predict(preprocessed)

    prediction_logger.log_prediction(
        user_id=session["user_id"],
        image_name=filename,
        disease_name=result.disease_name,
        confidence=result.confidence,
        treatment_advice=result.treatment_advice,
    )

    disease_name = result.disease_name
    if "___" in disease_name:
        plant_name, short_disease = disease_name.split("___", 1)
    else:
        plant_name, short_disease = "Plant", disease_name

    symptoms = SYMPTOM_MAP.get(
        disease_name,
        ["Visible leaf discoloration", "Localized spots", "Potential disease progression"],
    )

    sev_class = "low" if "healthy" in disease_name.lower() else ("high" if result.confidence >= 85 else "med")
    sev_label = "Healthy" if sev_class == "low" and "healthy" in disease_name.lower() else ("High" if sev_class == "high" else "Medium")

    return jsonify(
        {
            "disease_name": short_disease.replace("_", " "),
            "raw_class_name": disease_name,
            "plant_name": plant_name.replace("_", " "),
            "confidence": round(result.confidence, 2),
            "severity": sev_label,
            "severity_class": sev_class,
            "symptoms": symptoms,
            "treatment": [result.treatment_advice],
            "model": "EfficientNetB0",
            "processing": "OpenCV + CNN",
            "dataset": "PlantVillage",
            "image_name": filename,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
