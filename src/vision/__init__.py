"""Vision module exports for perception layer."""

from .hand_tracker import HandTracker  # Legacy (gesture control)
from .face_tracker import FaceTracker, FaceDetectionResult, FaceBoundingBox

__all__ = ["HandTracker", "FaceTracker", "FaceDetectionResult", "FaceBoundingBox"]
