"""
Emotion logic: convert geometric facial features into deterministic emotion labels.

Design goals:
- CPU-friendly geometric features (no training)
- Explainable thresholds that are interview-ready
- Decoupled from perception so rules can be tested offline
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

from src.vision.face_tracker import FaceBoundingBox


class Emotion(str, Enum):
    """Supported high-level emotions for the demo."""

    HAPPY = "HAPPY"
    SAD = "SAD"
    ANGRY = "ANGRY"
    SURPRISED = "SURPRISED"
    FEAR = "FEAR"
    DISGUST = "DISGUST"
    EXCITED = "EXCITED"
    NEUTRAL = "NEUTRAL"


@dataclass
class FacialFeatures:
    """Normalized geometric features extracted from landmarks."""

    mouth_openness: float  # Larger when the jaw drops or corners lift
    eye_openness: float  # Larger when eyes widen; smaller when squinting
    eyebrow_raise: float  # Positive when brows lift; negative when furrowed
    smile_lift: float  # Upward movement of mouth corners


class EmotionLogic:
    """Rule-based emotion inference built on lightweight facial geometry."""

    def __init__(self) -> None:
        # Tunable heuristics; calibrated for real-world facial expressions.
        self._mouth_open_happy = 0.015  # Balanced: smile + width
        self._mouth_open_excited = 0.035  # Bigger smile + open eyes
        self._mouth_open_surprised = 0.08  # Wide mouth for surprise
        self._mouth_open_fear = 0.05
        self._eye_open_neutral = 0.025  # Normal eye opening
        self._eye_open_excited = 0.032
        self._eye_open_surprised = 0.04  # Wide eyes
        self._eye_open_fear = 0.035
        self._eye_open_angry = 0.018  # Squinting
        self._brow_neutral_baseline = 0.05  # Typical brow-eye distance
        self._brow_raise_surprised = 0.008  # Eyebrows raised
        self._brow_raise_fear = 0.004
        self._brow_furrow_angry = -0.01  # Eyebrows lowered

    def compute_features(
        self,
        landmarks: List[Tuple[float, float, float]],
        bbox: FaceBoundingBox,
    ) -> FacialFeatures:
        """Compute normalized facial features from mesh landmarks.

        Args:
            landmarks: Normalized landmark list from FaceLandmarker (478 landmarks)
            bbox: Normalized bounding box of the detected face

        Returns:
            FacialFeatures with values normalized by face height to stay scale-invariant.
        """
        face_height = max(bbox.y_max - bbox.y_min, 1e-6)
        face_width = max(bbox.x_max - bbox.x_min, 1e-6)

        def norm_dist(idx1: int, idx2: int) -> float:
            p1, p2 = landmarks[idx1], landmarks[idx2]
            return math.dist((p1[0], p1[1]), (p2[0], p2[1])) / face_height

        # Mouth openness: Use proper mouth landmarks
        # Upper lip center: 13, Lower lip center: 14 (outer)
        # Inner mouth: top 13, bottom 14
        mouth_top = landmarks[13]  # Upper lip
        mouth_bottom = landmarks[14]  # Lower lip
        mouth_left = landmarks[61]  # Left mouth corner
        mouth_right = landmarks[291]  # Right mouth corner
        
        # Smile detection: mouth corners lift when smiling.
        # Y increases downward, so (corner - top) is positive when corners go UP.
        left_corner_lift = (mouth_left[1] - mouth_top[1]) / face_height
        right_corner_lift = (mouth_right[1] - mouth_top[1]) / face_height
        smile_lift = max((left_corner_lift + right_corner_lift) / 2.0, 0.0)
        
        # Use both vertical opening and horizontal width for better detection
        mouth_height = abs(mouth_bottom[1] - mouth_top[1]) / face_height
        mouth_width = abs(mouth_right[0] - mouth_left[0]) / face_width
        
        # Combine mouth height + smile lift + width for robust detection
        mouth_openness = max(0.0, (mouth_height * 2.5) + (smile_lift * 10.0) + (mouth_width * 0.4))

        # Eye openness: use eye aspect ratio approach
        # Left eye: top (159), bottom (145)
        # Right eye: top (386), bottom (374)
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        right_eye_top = landmarks[386]
        right_eye_bottom = landmarks[374]
        
        left_eye_open = abs(left_eye_top[1] - left_eye_bottom[1]) / face_height
        right_eye_open = abs(right_eye_top[1] - right_eye_bottom[1]) / face_height
        eye_openness = (left_eye_open + right_eye_open) / 2.0

        # Eyebrow raise: distance between eyebrow and eye
        # Use center of eyebrows for better tracking
        # Left: brow center (107), eye (159)
        # Right: brow center (336), eye (386)
        left_brow = landmarks[107] if len(landmarks) > 107 else landmarks[70]
        left_eye_ref = landmarks[159]
        right_brow = landmarks[336] if len(landmarks) > 336 else landmarks[300]
        right_eye_ref = landmarks[386]
        
        left_brow_dist = abs(left_eye_ref[1] - left_brow[1]) / face_height
        right_brow_dist = abs(right_eye_ref[1] - right_brow[1]) / face_height
        brow_gap = (left_brow_dist + right_brow_dist) / 2.0
        eyebrow_raise = brow_gap - self._brow_neutral_baseline

        return FacialFeatures(
            mouth_openness=mouth_openness,
            eye_openness=eye_openness,
            eyebrow_raise=eyebrow_raise,
            smile_lift=smile_lift,
        )

    def infer_emotion(self, features: FacialFeatures) -> Emotion:
        """Map geometric features to a stable, explainable emotion label."""
        # Guard 1: tiny movements → Neutral
        if (
            features.mouth_openness < self._mouth_open_happy * 0.25
            and abs(features.eyebrow_raise) < 0.003
            and features.eye_openness < self._eye_open_neutral * 1.1
        ):
            return Emotion.NEUTRAL

        # Guard 2: speech (mouth open without smiling) → keep neutral
        if (
            features.smile_lift < 0.008
            and features.mouth_openness > self._mouth_open_happy * 1.2
            and self._eye_open_neutral * 0.6 < features.eye_openness < self._eye_open_surprised
        ):
            return Emotion.NEUTRAL
        # Excited: big smile + open eyes + raised brows
        if (
            features.smile_lift > 0.022
            and features.mouth_openness > self._mouth_open_excited * 0.95
            and features.eye_openness > self._eye_open_excited * 0.95
            and features.eyebrow_raise > -0.001
        ):
            return Emotion.EXCITED

        # Happy: clear smile and relaxed/wide eyes
        if (
            features.smile_lift > 0.012
            and features.mouth_openness > self._mouth_open_happy * 1.05
            and features.eye_openness >= self._eye_open_neutral * 0.8  # avoid speech false positives
        ):
            return Emotion.HAPPY

        # Surprise: wide mouth, wide eyes, brows up (all three conditions), but not smiling
        effective_surprise_mouth = features.mouth_openness - (features.smile_lift * 6.0)
        if (
            effective_surprise_mouth > self._mouth_open_surprised * 1.08
            and features.eye_openness > self._eye_open_surprised * 0.98
            and features.eyebrow_raise > self._brow_raise_surprised * 1.12
            and features.smile_lift < 0.006  # strong anti-smile gate
        ):
            return Emotion.SURPRISED

        # Fear: wide eyes + moderately open mouth + brows raised, but not smiling
        if (
            features.mouth_openness > self._mouth_open_fear * 1.05
            and features.eye_openness > self._eye_open_fear
            and features.eyebrow_raise > self._brow_raise_fear * 1.05
            and features.smile_lift < 0.008
        ):
            return Emotion.FEAR

        # Angry: brows down + squinting
        if (
            features.eyebrow_raise < self._brow_furrow_angry
            and features.eye_openness < self._eye_open_angry
        ):
            return Emotion.ANGRY

        # Disgust: mouth moderately open, slight brow lower, eyes not too wide
        if (
            self._mouth_open_happy * 0.5 < features.mouth_openness < self._mouth_open_surprised * 0.9
            and features.eye_openness < self._eye_open_neutral * 0.9
            and features.eyebrow_raise < -0.002
            and features.smile_lift < 0.01
        ):
            return Emotion.DISGUST

        # Sad: mouth closed, eyes narrowed or normal, brows slightly up
        if (
            features.mouth_openness < self._mouth_open_happy * 0.5
            and features.eye_openness < self._eye_open_neutral * 1.05
            and features.eyebrow_raise > -0.004
        ):
            return Emotion.SAD

        return Emotion.NEUTRAL
