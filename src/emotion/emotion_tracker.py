"""
Emotion Tracker: Temporal smoothing and confidence scoring for stable emotion detection.

Award-winning features:
- Exponential moving average for jitter-free emotion tracking
- Confidence scoring based on feature stability
- Emotion history for analytics and visualization
"""

from collections import deque
from dataclasses import dataclass
from typing import Deque, Optional

from .emotion_logic import Emotion, FacialFeatures


@dataclass
class EmotionState:
    """Represents the current emotion state with confidence."""
    emotion: Emotion
    confidence: float
    raw_features: FacialFeatures
    smoothed_features: FacialFeatures


class EmotionTracker:
    """
    Tracks emotions over time with temporal smoothing for production-grade stability.
    
    Key features:
    - Exponential moving average prevents jitter
    - Confidence scoring prevents false positives
    - History tracking enables analytics
    """
    
    def __init__(
        self,
        smoothing_factor: float = 0.3,
        history_size: int = 100,
        confidence_threshold: float = 0.7,
        min_dwell_frames: int = 4,
        cooldown_frames: int = 6,
    ) -> None:
        """
        Args:
            smoothing_factor: EMA alpha (0=smooth, 1=responsive). 0.3 is balanced.
            history_size: Number of past emotions to track for analytics
            confidence_threshold: Minimum confidence to change emotion
        """
        self._smoothing_factor = smoothing_factor
        self._confidence_threshold = confidence_threshold
        self._min_dwell_frames = min_dwell_frames
        self._cooldown_frames = cooldown_frames
        
        # Smoothed feature values
        self._mouth_ema: Optional[float] = None
        self._eye_ema: Optional[float] = None
        self._brow_ema: Optional[float] = None
        self._smile_ema: Optional[float] = None
        
        # Current state
        self._current_emotion = Emotion.NEUTRAL
        self._emotion_stability_count = 0
        self._current_hold_frames = 0
        self._cooldown_remaining = 0
        self._pending_emotion: Optional[Emotion] = None
        self._pending_count = 0
        
        # History tracking for analytics
        self._emotion_history: Deque[Emotion] = deque(maxlen=history_size)
        self._feature_variance_window: Deque[FacialFeatures] = deque(maxlen=10)
    
    def update(self, features: FacialFeatures, detected_emotion: Emotion) -> EmotionState:
        """
        Update tracker with new features and get smoothed emotion state.
        
        Args:
            features: Raw facial features from current frame
            detected_emotion: Raw emotion inference from logic layer
            
        Returns:
            EmotionState with smoothed features and confidence score
        """
        # Initialize EMA on first frame
        if self._mouth_ema is None:
            self._mouth_ema = features.mouth_openness
            self._eye_ema = features.eye_openness
            self._brow_ema = features.eyebrow_raise
            self._smile_ema = features.smile_lift

        # Type narrowing for static analysis (all EMAs are guaranteed set here)
        assert self._mouth_ema is not None
        assert self._eye_ema is not None
        assert self._brow_ema is not None
        assert self._smile_ema is not None
        
        # Apply exponential moving average
        alpha = self._smoothing_factor
        self._mouth_ema = alpha * features.mouth_openness + (1 - alpha) * self._mouth_ema
        self._eye_ema = alpha * features.eye_openness + (1 - alpha) * self._eye_ema
        self._brow_ema = alpha * features.eyebrow_raise + (1 - alpha) * self._brow_ema
        self._smile_ema = alpha * features.smile_lift + (1 - alpha) * self._smile_ema
        
        smoothed_features = FacialFeatures(
            mouth_openness=self._mouth_ema,
            eye_openness=self._eye_ema,
            eyebrow_raise=self._brow_ema,
            smile_lift=self._smile_ema,
        )
        
        # Track feature variance for confidence scoring
        self._feature_variance_window.append(features)
        confidence = self._compute_confidence()

        # Safety net: when signal is shaky, default to NEUTRAL to avoid false spikes
        if confidence < 0.45:
            detected_emotion = Emotion.NEUTRAL
        
        # Update emotion with dwell + cooldown to prevent rapid flipping
        if detected_emotion == self._current_emotion:
            self._emotion_stability_count = min(self._emotion_stability_count + 1, 10)
            self._current_hold_frames += 1
            self._pending_emotion = None
            self._pending_count = 0
            self._cooldown_remaining = max(self._cooldown_remaining - 1, 0)
        else:
            # Track candidate emotion across frames
            if self._pending_emotion == detected_emotion:
                self._pending_count += 1
            else:
                self._pending_emotion = detected_emotion
                self._pending_count = 1

            if (
                confidence >= self._confidence_threshold
                and self._pending_count >= self._min_dwell_frames
                and self._cooldown_remaining == 0
            ):
                self._current_emotion = detected_emotion
                self._emotion_stability_count = 5  # Start with medium stability
                self._current_hold_frames = 0
                self._cooldown_remaining = self._cooldown_frames
            elif self._emotion_stability_count > 0:
                self._emotion_stability_count -= 1
        
        # Record to history
        self._emotion_history.append(self._current_emotion)
        
        return EmotionState(
            emotion=self._current_emotion,
            confidence=confidence,
            raw_features=features,
            smoothed_features=smoothed_features,
        )
    
    def _compute_confidence(self) -> float:
        """
        Compute confidence score based on feature stability.
        
        High confidence = stable features (low variance)
        Low confidence = jittery features (high variance)
        """
        if len(self._feature_variance_window) < 5:
            return 0.5  # Not enough data
        
        # Calculate variance in recent features
        mouth_vals = [f.mouth_openness for f in self._feature_variance_window]
        eye_vals = [f.eye_openness for f in self._feature_variance_window]
        brow_vals = [f.eyebrow_raise for f in self._feature_variance_window]
        smile_vals = [f.smile_lift for f in self._feature_variance_window]
        
        def variance(vals):
            mean = sum(vals) / len(vals)
            return sum((x - mean) ** 2 for x in vals) / len(vals)
        
        mouth_var = variance(mouth_vals)
        eye_var = variance(eye_vals)
        brow_var = variance(brow_vals)
        smile_var = variance(smile_vals)
        
        # Lower variance = higher confidence
        # Use sigmoid-like mapping: confidence = 1 / (1 + variance * scale)
        total_var = mouth_var * 80 + eye_var * 40 + brow_var * 40 + smile_var * 120
        confidence = 1.0 / (1.0 + total_var)
        
        return min(max(confidence, 0.0), 1.0)
    
    def get_emotion_stats(self) -> dict:
        """Get analytics on emotion distribution over history."""
        if not self._emotion_history:
            return {}
        
        total = len(self._emotion_history)
        stats = {}
        for emotion in Emotion:
            count = self._emotion_history.count(emotion)
            stats[emotion.value] = {
                'count': count,
                'percentage': (count / total) * 100 if total > 0 else 0
            }
        return stats
    
    def reset(self) -> None:
        """Reset tracker state."""
        self._mouth_ema = None
        self._eye_ema = None
        self._brow_ema = None
        self._smile_ema = None
        self._current_emotion = Emotion.NEUTRAL
        self._emotion_stability_count = 0
        self._current_hold_frames = 0
        self._cooldown_remaining = 0
        self._pending_emotion = None
        self._pending_count = 0
        self._emotion_history.clear()
        self._feature_variance_window.clear()
