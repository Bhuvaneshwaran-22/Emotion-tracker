"""Lightweight CSV logger for per-frame emotion features.

This module stays decoupled from visualization and logic. It can be toggled
at runtime to capture feature traces for benchmarking and calibration.
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Optional

from src.emotion.emotion_logic import Emotion
from src.emotion.emotion_logic import FacialFeatures


class FeatureLogger:
    """CSV logger for benchmark mode.

    Each row captures timestamped features and the system's output.
    """

    def __init__(self, log_path: Optional[Path] = None) -> None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        self._path = log_path or Path("logs") / f"emotion_log_{ts}.csv"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(
            [
                "timestamp_s",
                "fps",
                "mouth_openness",
                "eye_openness",
                "eyebrow_raise",
                "smile_lift",
                "emotion",
                "confidence",
            ]
        )

    @property
    def path(self) -> Path:
        return self._path

    def log(self, *, fps: float, features: FacialFeatures, emotion: Emotion, confidence: float) -> None:
        """Append one frame of data to the CSV."""
        now = time.time()
        self._writer.writerow(
            [
                f"{now:.6f}",
                f"{fps:.3f}",
                f"{features.mouth_openness:.6f}",
                f"{features.eye_openness:.6f}",
                f"{features.eyebrow_raise:.6f}",
                f"{features.smile_lift:.6f}",
                emotion.value,
                f"{confidence:.4f}",
            ]
        )

    def close(self) -> None:
        if not self._file.closed:
            self._file.flush()
            self._file.close()

    def __enter__(self) -> "FeatureLogger":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
