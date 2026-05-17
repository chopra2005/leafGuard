# Plant Disease Detection System

This project detects plant leaf diseases from uploaded images using image preprocessing, a CNN classifier (EfficientNetB0), and a Flask web app.

## Development Order (Aligned to Timeline)

1. Dataset collection (Completed)
2. OpenCV preprocessing (`src/preprocessing/pipeline.py`)
3. EfficientNetB0 training notebook/script (Weeks 4-5)
4. Flask app integration (`src/app.py`)
5. Database logging and UI polish (`src/db/logger.py`, `templates/`, `static/`)
6. Testing, report, and PPT

## Project Structure

- `src/preprocessing/pipeline.py` - image resize, denoise, and leaf segmentation
- `src/inference/model_service.py` - EfficientNetB0 model loading and prediction logic
- `train_efficientnet.py` - EfficientNetB0 training script
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

1. Train and save model as `models/plant_disease_efficientnetb0.keras`
2. Start app:

```bash
python src/app.py
```

3. Open browser at:
- `http://127.0.0.1:5000`

## Deploy

The project is ready for a Python web service such as Render.

1. Make sure `models/plant_disease_efficientnetb0.keras` and `models/class_names.json` are committed with the project.
2. Push the project to GitHub.
3. Create a new Render Web Service from the GitHub repository.
4. Use these settings:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --timeout 180`
   - Python version: `3.11.9`
5. Add an environment variable:
   - `FLASK_SECRET_KEY`: any long random value

The included `render.yaml`, `Procfile`, `runtime.txt`, and `wsgi.py` provide the same deployment settings.

## Notes

- Update `src/config.py` with all class names from your trained model.
- Update `TREATMENT_MAP` for each disease class.
