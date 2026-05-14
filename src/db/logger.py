from __future__ import annotations

import sqlite3
from pathlib import Path


class PredictionLogger:
    def __init__(self, db_path: str | Path = "predictions.db") -> None:
        self.db_path = str(db_path)
        self._initialize_db()

    def _initialize_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prediction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_name TEXT NOT NULL,
                    disease_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    treatment_advice TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def log_prediction(self, image_name: str, disease_name: str, confidence: float, treatment_advice: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO prediction_logs (image_name, disease_name, confidence, treatment_advice)
                VALUES (?, ?, ?, ?)
                """,
                (image_name, disease_name, confidence, treatment_advice),
            )

    def get_all_predictions(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prediction_logs ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM prediction_logs")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT disease_name, COUNT(*) as count FROM prediction_logs GROUP BY disease_name ORDER BY count DESC LIMIT 5")
            top_diseases = cursor.fetchall()
            
            return {
                "total_predictions": total,
                "top_diseases": top_diseases
            }
