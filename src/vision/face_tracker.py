"""
Face Tracker Module - MediaPipe Tasks (FaceLandmarker) for emotion analysis.

Responsibilities:
- Detect faces via MediaPipe FaceLandmarker (CPU-friendly)
- Output normalized landmarks and bounding boxes for downstream logic
- Optionally draw landmarks for visual debugging
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import mediapipe as mp  # type: ignore[attr-defined]
import numpy as np


@dataclass
class FaceBoundingBox:
    """Normalized bounding box coordinates for a detected face."""
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass
class FaceDetectionResult:
    """Structured face detection output used by downstream emotion logic."""
    landmarks: List[Tuple[float, float, float]]  # Normalized face mesh points
    bbox: FaceBoundingBox  # Normalized bounding box
    detection_confidence: float  # Tasks API does not expose a score; set to 1.0


class FaceTracker:
    """Wrapper around MediaPipe Tasks FaceLandmarker for real-time webcam inference."""

    def __init__(
        self,
        max_faces: int = 1,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.6,
        draw_landmarks: bool = False,
        model_path: Optional[Path] = None,
    ) -> None:
        self._draw_landmarks = draw_landmarks
        self._max_faces = max_faces

        # Resolve model path and download if missing
        self._model_path = model_path or Path(__file__).resolve().parent.parent / "assets" / "face_landmarker.task"
        self._ensure_model(self._model_path)

        base_options = mp.tasks.BaseOptions(
            model_asset_path=str(self._model_path),
            delegate=mp.tasks.BaseOptions.Delegate.CPU,
        )

        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_faces=self._max_faces,
            min_face_detection_confidence=min_detection_confidence,
            min_face_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        self._landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
        self._frame_count = 0

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[List[FaceDetectionResult]]]:
        """Detect faces and return landmarks plus optional debug rendering."""
        if frame is None:
            return frame, None

        self._frame_count += 1
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = self._frame_count * 33  # assume ~30 FPS
        results = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        annotated_frame = frame.copy()
        if not results.face_landmarks:
            return annotated_frame, None

        h, w, _ = frame.shape
        faces: List[FaceDetectionResult] = []

        for face_landmarks in results.face_landmarks:
            landmarks = [(lm.x, lm.y, lm.z) for lm in face_landmarks]
            bbox = self._landmarks_to_bbox(landmarks)
            faces.append(
                FaceDetectionResult(
                    landmarks=landmarks,
                    bbox=bbox,
                    detection_confidence=1.0,
                )
            )

            if self._draw_landmarks:
                self._draw_points(annotated_frame, landmarks, w, h)

        return annotated_frame, faces

    def _draw_points(self, image: np.ndarray, landmarks: List[Tuple[float, float, float]], width: int, height: int) -> None:
        """Lightweight landmark drawing for debugging without extra deps."""
        for lm in landmarks:
            x = int(lm[0] * width)
            y = int(lm[1] * height)
            cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

    def _landmarks_to_bbox(self, landmarks: List[Tuple[float, float, float]]) -> FaceBoundingBox:
        """Derive a normalized bounding box from face mesh landmarks."""
        coords = np.array([(lm[0], lm[1]) for lm in landmarks])
        x_min, y_min = np.min(coords, axis=0)
        x_max, y_max = np.max(coords, axis=0)
        return FaceBoundingBox(
            x_min=float(x_min),
            y_min=float(y_min),
            x_max=float(x_max),
            y_max=float(y_max),
        )

    def _ensure_model(self, model_path: Path) -> None:
        """Download the face landmarker model if it does not exist."""
        if model_path.exists():
            return
        model_path.parent.mkdir(parents=True, exist_ok=True)
        url = (
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
            "face_landmarker/float16/1/face_landmarker.task"
        )
        print(f"Downloading face landmarker model to {model_path} ...")
        from urllib.request import urlretrieve

        urlretrieve(url, model_path)
        print("✓ Face model downloaded")

    def release(self) -> None:
        """Release MediaPipe resources cleanly."""
        if hasattr(self, "_landmarker") and self._landmarker:
            close_fn = getattr(self._landmarker, "close", None)
            if callable(close_fn):
                close_fn()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __del__(self):
        self.release()
