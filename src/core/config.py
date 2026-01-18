"""Configuration loader for AIRCTRL.

Loads settings from config.yaml and provides defaults if missing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class CameraConfig:
    index: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 30


@dataclass
class FaceDetectionConfig:
    max_faces: int = 1
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.7
    draw_landmarks: bool = False


@dataclass
class EmotionThresholds:
    mouth_open_happy: float = 0.015
    mouth_open_excited: float = 0.035
    mouth_open_surprised: float = 0.08
    mouth_open_fear: float = 0.05
    eye_open_neutral: float = 0.025
    eye_open_excited: float = 0.032
    eye_open_surprised: float = 0.04
    eye_open_fear: float = 0.035
    eye_open_angry: float = 0.018
    brow_neutral_baseline: float = 0.05
    brow_raise_surprised: float = 0.008
    brow_raise_fear: float = 0.004
    brow_furrow_angry: float = -0.01


@dataclass
class SmoothingConfig:
    smoothing_factor: float = 0.3
    history_size: int = 100
    confidence_threshold: float = 0.6
    min_dwell_frames: int = 4
    cooldown_frames: int = 6


@dataclass
class UIConfig:
    emoji_scale: float = 0.65
    fps_light_mode_threshold: float = 15.0
    show_confidence_on_bbox: bool = True


@dataclass
class LoggingConfig:
    enabled: bool = False
    log_path: Optional[str] = None


@dataclass
class Config:
    camera: CameraConfig
    face_detection: FaceDetectionConfig
    emotion_thresholds: EmotionThresholds
    smoothing: SmoothingConfig
    ui: UIConfig
    logging: LoggingConfig


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file with defaults."""
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    
    if not config_path.exists():
        print(f"⚠️  Config not found at {config_path}, using defaults")
        return Config(
            camera=CameraConfig(),
            face_detection=FaceDetectionConfig(),
            emotion_thresholds=EmotionThresholds(),
            smoothing=SmoothingConfig(),
            ui=UIConfig(),
            logging=LoggingConfig(),
        )
    
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return Config(
        camera=CameraConfig(**data.get("camera", {})),
        face_detection=FaceDetectionConfig(**data.get("face_detection", {})),
        emotion_thresholds=EmotionThresholds(**data.get("emotion_thresholds", {})),
        smoothing=SmoothingConfig(**data.get("smoothing", {})),
        ui=UIConfig(**data.get("ui", {})),
        logging=LoggingConfig(**data.get("logging", {})),
    )
