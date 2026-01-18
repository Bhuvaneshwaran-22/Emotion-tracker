"""Calibration helpers for rule-based thresholds.

These utilities summarize logged features and propose threshold adjustments
without introducing any learned models. Intended for offline tuning.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class FeatureStats:
    mean: float
    std: float
    min: float
    max: float


@dataclass
class CalibrationSuggestion:
    mouth_open_happy: float
    mouth_open_surprised: float
    eye_open_surprised: float
    eye_open_fear: float
    brow_raise_surprised: float
    brow_furrow_angry: float


def summarize_log(log_path: Path) -> Dict[str, FeatureStats]:
    """Compute basic stats from a CSV log produced by FeatureLogger."""
    columns: Dict[str, List[float]] = {
        "mouth_openness": [],
        "eye_openness": [],
        "eyebrow_raise": [],
        "smile_lift": [],
    }

    with log_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in columns:
                try:
                    columns[key].append(float(row[key]))
                except (KeyError, ValueError):
                    continue

    stats: Dict[str, FeatureStats] = {}
    for key, values in columns.items():
        if not values:
            continue
        n = len(values)
        mean = sum(values) / n
        var = sum((v - mean) ** 2 for v in values) / n
        std = var ** 0.5
        stats[key] = FeatureStats(mean=mean, std=std, min=min(values), max=max(values))
    return stats


def suggest_thresholds(stats: Dict[str, FeatureStats]) -> CalibrationSuggestion:
    """Suggest updated thresholds using simple statistical heuristics.

    Strategy (interview-ready):
    - Happy mouth: slightly above average mouth openness to avoid speech.
    - Surprise mouth: near the high tail to avoid false positives.
    - Eye surprise/fear: high percentile to detect real widening.
    - Brow raise surprise: mean + std to require lift.
    - Brow furrow angry: below mean to catch downward brows.
    """
    def get(key: str) -> FeatureStats:
        if key not in stats:
            raise ValueError(f"Missing stats for {key}")
        return stats[key]

    mouth = get("mouth_openness")
    eye = get("eye_openness")
    brow = get("eyebrow_raise")

    return CalibrationSuggestion(
        mouth_open_happy=mouth.mean + mouth.std * 0.3,
        mouth_open_surprised=mouth.max * 0.9,
        eye_open_surprised=eye.mean + eye.std * 0.8,
        eye_open_fear=eye.mean + eye.std * 0.6,
        brow_raise_surprised=brow.mean + brow.std * 1.0,
        brow_furrow_angry=brow.mean - abs(brow.std * 0.7),
    )
