from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from tensorflow.keras.models import load_model


@dataclass
class PredictionResult:
    disease_name: str
    confidence: float
    treatment_advice: str


class PlantDiseaseModelService:
    def __init__(self, model_path: str | Path, class_names: list[str], treatment_map: dict[str, str]) -> None:
        self.model = load_model(str(model_path))
        self.class_names = class_names
        self.treatment_map = treatment_map

    def predict(self, preprocessed_rgb: np.ndarray) -> PredictionResult:
        image = preprocessed_rgb.astype("float32") / 255.0
        batch = np.expand_dims(image, axis=0)
        probs = self.model.predict(batch, verbose=0)[0]

        class_idx = int(np.argmax(probs))
        confidence = float(probs[class_idx] * 100.0)
        disease_name = self.class_names[class_idx]
        treatment_advice = self.treatment_map.get(
            disease_name,
            "Isolate affected plant and consult agricultural expert for targeted treatment.",
        )

        return PredictionResult(
            disease_name=disease_name,
            confidence=confidence,
            treatment_advice=treatment_advice,
        )
