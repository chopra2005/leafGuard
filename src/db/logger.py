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
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prediction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    image_name TEXT NOT NULL,
                    disease_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    treatment_advice TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            try:
                conn.execute("ALTER TABLE prediction_logs ADD COLUMN user_id INTEGER")
            except sqlite3.OperationalError:
                pass

    def create_user(self, username: str, password_hash: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
                return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_username(self, username: str) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def log_prediction(self, user_id: int, image_name: str, disease_name: str, confidence: float, treatment_advice: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO prediction_logs (user_id, image_name, disease_name, confidence, treatment_advice)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, image_name, disease_name, confidence, treatment_advice),
            )

    def get_all_predictions(self, user_id: int) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prediction_logs WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_stats(self, user_id: int) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM prediction_logs WHERE user_id = ?", (user_id,))
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT disease_name, COUNT(*) as count FROM prediction_logs WHERE user_id = ? GROUP BY disease_name ORDER BY count DESC LIMIT 5", (user_id,))
            top_diseases = cursor.fetchall()
            
            return {
                "total_predictions": total,
                "top_diseases": top_diseases
            }
