"""
Emoji mapper: map emotion labels to emoji assets and overlay them on frames.

Responsibilities:
- Load emoji PNGs with alpha transparency
- Provide graceful placeholders if assets are missing
- Overlay scaled emoji near detected faces without hiding the person
"""

from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np

from .emotion_logic import Emotion
from src.vision.face_tracker import FaceBoundingBox


class EmojiMapper:
    """Handles loading and rendering emoji overlays for the visualization layer."""

    def __init__(self, emoji_dir: Path) -> None:
        self.emoji_dir = emoji_dir
        self.emoji_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[Emotion, np.ndarray] = {}

    def get_emoji(self, emotion: Emotion) -> np.ndarray:
        """Return an emoji image (RGBA). Generates a placeholder if missing."""
        if emotion in self._cache:
            return self._cache[emotion]

        path = self.emoji_dir / f"{emotion.value.lower()}.png"
        if path.exists():
            img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        else:
            img = None

        if img is None:
            img = self._generate_placeholder(emotion)

        # Ensure 4 channels for alpha blending
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

        self._cache[emotion] = img
        return img

    def overlay_emoji(
        self,
        frame: np.ndarray,
        emoji_img: Optional[np.ndarray],
        bbox: FaceBoundingBox,
        scale: float = 0.6,
    ) -> np.ndarray:
        """Overlay an emoji near the face using alpha blending."""
        if emoji_img is None:
            return frame

        h, w, _ = frame.shape
        face_w = max((bbox.x_max - bbox.x_min) * w, 1.0)

        target_w = int(face_w * scale)
        target_h = int(target_w * (emoji_img.shape[0] / emoji_img.shape[1]))
        resized = cv2.resize(emoji_img, (target_w, target_h), interpolation=cv2.INTER_AREA)

        # Position above and to the right of the face for better visibility
        x0 = int(bbox.x_max * w) + 10
        y0 = int(bbox.y_min * h)
        # Fallback: if too far right, place above
        if x0 + target_w > w:
            x0 = int(bbox.x_min * w)
            y0 = int(bbox.y_min * h) - target_h - 10
            if y0 < 0:
                y0 = 10

        x1 = min(x0 + target_w, w)
        y1 = min(y0 + target_h, h)
        x0 = max(x0, 0)
        y0 = max(y0, 0)

        roi = frame[y0:y1, x0:x1]
        resized = resized[: y1 - y0, : x1 - x0]

        if resized.shape[0] == 0 or resized.shape[1] == 0:
            return frame

        alpha = resized[:, :, 3] / 255.0
        alpha_inv = 1.0 - alpha

        for c in range(3):
            roi[:, :, c] = (alpha * resized[:, :, c] + alpha_inv * roi[:, :, c]).astype(roi.dtype)

        frame[y0:y1, x0:x1] = roi
        return frame

    def _generate_placeholder(self, emotion: Emotion) -> np.ndarray:
        """Create attractive emoji-style placeholders with facial features."""
        size = 240
        canvas = np.zeros((size, size, 4), dtype=np.uint8)
        center = (size // 2, size // 2)
        radius = size // 2 - 15

        # Color schemes for each emotion
        color_map = {
            Emotion.HAPPY: (50, 220, 120),       # Bright green
            Emotion.SAD: (230, 180, 100),        # Blue-ish
            Emotion.ANGRY: (50, 50, 240),        # Red
            Emotion.SURPRISED: (100, 200, 255),  # Yellow-orange
            Emotion.FEAR: (180, 160, 255),       # Pale purple
            Emotion.DISGUST: (100, 200, 120),    # Greenish
            Emotion.EXCITED: (255, 170, 90),     # Warm orange
            Emotion.NEUTRAL: (220, 220, 220),    # Light gray
        }
        
        base_color = color_map.get(emotion, (220, 220, 220))
        
        # Draw main face circle with gradient effect
        cv2.circle(canvas, center, radius, (*base_color, 255), -1)
        cv2.circle(canvas, center, radius, (255, 255, 255, 255), 4)
        
        # Add slight highlight for 3D effect
        highlight_center = (center[0] - radius // 3, center[1] - radius // 3)
        cv2.circle(canvas, highlight_center, radius // 3, (255, 255, 255, 80), -1)
        
        # Draw eyes and mouth based on emotion
        eye_y = center[1] - radius // 4
        left_eye_x = center[0] - radius // 3
        right_eye_x = center[0] + radius // 3
        eye_radius = radius // 10
        
        mouth_y = center[1] + radius // 3
        mouth_width = radius // 2
        
        if emotion == Emotion.HAPPY:
            # Smiling eyes (^_^)
            cv2.ellipse(canvas, (left_eye_x, eye_y), (eye_radius, eye_radius // 2), 
                       0, 0, 180, (0, 0, 0, 255), 3)
            cv2.ellipse(canvas, (right_eye_x, eye_y), (eye_radius, eye_radius // 2), 
                       0, 0, 180, (0, 0, 0, 255), 3)
            # Big smile
            cv2.ellipse(canvas, (center[0], mouth_y), (mouth_width, mouth_width // 2), 
                       0, 0, 180, (0, 0, 0, 255), 4)
                       
        elif emotion == Emotion.SAD:
            # Sad eyes
            cv2.circle(canvas, (left_eye_x, eye_y), eye_radius, (0, 0, 0, 255), 3)
            cv2.circle(canvas, (right_eye_x, eye_y), eye_radius, (0, 0, 0, 255), 3)
            # Frown
            cv2.ellipse(canvas, (center[0], mouth_y + 15), (mouth_width, mouth_width // 2), 
                       0, 180, 360, (0, 0, 0, 255), 4)
            # Tear
            cv2.circle(canvas, (left_eye_x + 10, eye_y + 20), 6, (100, 200, 255, 255), -1)
            
        elif emotion == Emotion.ANGRY:
            # Angry eyes
            cv2.circle(canvas, (left_eye_x, eye_y), eye_radius, (0, 0, 0, 255), -1)
            cv2.circle(canvas, (right_eye_x, eye_y), eye_radius, (0, 0, 0, 255), -1)
            # Angry brows
            cv2.line(canvas, (left_eye_x - 15, eye_y - 15), (left_eye_x + 15, eye_y - 5), 
                    (0, 0, 0, 255), 4)
            cv2.line(canvas, (right_eye_x - 15, eye_y - 5), (right_eye_x + 15, eye_y - 15), 
                    (0, 0, 0, 255), 4)
            # Angry mouth
            cv2.line(canvas, (center[0] - mouth_width, mouth_y), 
                    (center[0] + mouth_width, mouth_y), (0, 0, 0, 255), 4)
                    
        elif emotion == Emotion.SURPRISED:
            # Wide open eyes
            cv2.circle(canvas, (left_eye_x, eye_y), eye_radius + 3, (0, 0, 0, 255), 3)
            cv2.circle(canvas, (right_eye_x, eye_y), eye_radius + 3, (0, 0, 0, 255), 3)
            cv2.circle(canvas, (left_eye_x, eye_y), eye_radius // 2, (0, 0, 0, 255), -1)
            cv2.circle(canvas, (right_eye_x, eye_y), eye_radius // 2, (0, 0, 0, 255), -1)
            # Open mouth (O)
            cv2.ellipse(canvas, (center[0], mouth_y + 10), (mouth_width // 2, mouth_width), 
                       0, 0, 360, (0, 0, 0, 255), 4)
                       
        else:  # NEUTRAL
            # Normal eyes
            cv2.circle(canvas, (left_eye_x, eye_y), eye_radius, (0, 0, 0, 255), 3)
            cv2.circle(canvas, (right_eye_x, eye_y), eye_radius, (0, 0, 0, 255), 3)
            # Neutral mouth
            cv2.line(canvas, (center[0] - mouth_width // 2, mouth_y), 
                    (center[0] + mouth_width // 2, mouth_y), (0, 0, 0, 255), 3)
        
        # Add emotion label at bottom
        label = emotion.value
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = (size - text_size[0]) // 2
        text_y = size - 15
        
        # Text shadow for better visibility
        cv2.putText(canvas, label, (text_x + 2, text_y + 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0, 200), 2, cv2.LINE_AA)
        cv2.putText(canvas, label, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255, 255), 2, cv2.LINE_AA)
        
        return canvas
