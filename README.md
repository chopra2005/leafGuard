# Plant Disease Detection System

This project detects plant leaf diseases from uploaded images using OpenCV preprocessing, a CNN classifier (MobileNetV2), and a Flask web app.

## Development Order (Aligned to Timeline)

1. Dataset collection (Completed)
2. OpenCV preprocessing (`src/preprocessing/pipeline.py`)
3. MobileNetV2 training notebook (Weeks 4-5)
4. Flask app integration (`src/app.py`)
5. Database logging and UI polish (`src/db/logger.py`, `templates/`, `static/`)
6. Testing, report, and PPT

## Project Structure

- `src/preprocessing/pipeline.py` - image resize, denoise, and leaf segmentation
- `src/inference/model_service.py` - model loading and prediction logic
- `src/db/logger.py` - SQLite logging for predictions
- `src/app.py` - Flask app for uploading images and displaying results
- `templates/index.html` - frontend page
- `static/style.css` - basic styling
- `notebooks/README.md` - notebook training checklist

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Flask App

1. Train and save model as `models/plant_disease_mobilenetv2.keras`
2. Start app:

```bash
python src/app.py
```

3. Open browser at:
- `http://127.0.0.1:5000`

## Notes

- Update `src/config.py` with all class names from your trained model.
- Update `TREATMENT_MAP` for each disease class.
