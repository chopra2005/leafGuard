from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from config import CLASS_NAMES, SYMPTOM_MAP, TREATMENT_MAP
from db.logger import PredictionLogger
from inference.model_service import PlantDiseaseModelService
from preprocessing.pipeline import LeafPreprocessor

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
MODEL_PATH = BASE_DIR / "models" / "plant_disease_mobilenetv2.keras"

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    predictions = prediction_logger.get_all_predictions()
    stats = prediction_logger.get_stats()
    return render_template("dashboard.html", predictions=predictions, stats=stats)


@app.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("leaf_image")
    if not file or file.filename == "":
        return jsonify({"error": "Please upload a leaf image file."}), 400

    if not _is_allowed(file.filename):
        return jsonify({"error": "Only JPG, JPEG, and PNG files are supported."}), 400

    if model_service is None:
        return jsonify({"error": "Model file not found at models/plant_disease_mobilenetv2.keras."}), 500

    filename = secure_filename(file.filename)
    image_path = UPLOAD_DIR / filename
    file.save(image_path)

    preprocessed = preprocessor.preprocess_from_path(image_path)
    result = model_service.predict(preprocessed)

    prediction_logger.log_prediction(
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
            "model": "MobileNetV2",
            "processing": "OpenCV + CNN",
            "dataset": "PlantVillage",
            "image_name": filename,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
