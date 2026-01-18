"""
Hand Tracker Module - MediaPipe-based hand detection and landmark tracking.

This module provides a clean interface for detecting hands and tracking
21 hand landmarks using Google's MediaPipe framework (CPU-optimized).
"""

import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple, NamedTuple
from urllib.request import urlretrieve


class HandLandmark(NamedTuple):
    """Represents a single hand landmark point."""
    x: float  # Normalized x coordinate [0.0, 1.0]
    y: float  # Normalized y coordinate [0.0, 1.0]
    z: float  # Depth relative to wrist


class HandDetectionResult(NamedTuple):
    """Result of hand detection with landmarks."""
    landmarks: List[HandLandmark]
    handedness: str  # "Left" or "Right"
    confidence: float


class HandTracker:
    """
    Hand tracking class using MediaPipe Hands solution.
    
    Optimized for CPU-only execution on laptops with 16GB RAM.
    Detects up to 1 hand with 21 landmarks per hand.
    
    Attributes:
        max_hands (int): Maximum number of hands to detect (1 for performance)
        min_detection_confidence (float): Minimum confidence for detection
        min_tracking_confidence (float): Minimum confidence for tracking
    """
    
    def __init__(
        self,
        max_hands: int = 1,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5,
        model_path: Optional[Path] = None,
    ):
        """
        Initialize the hand tracker with MediaPipe.
        
        Args:
            max_hands: Maximum number of hands to detect (keep at 1 for CPU)
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        self.max_hands = max_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        # Resolve model path and download if missing
        self.model_path = model_path or Path(__file__).resolve().parent.parent / "assets" / "hand_landmarker.task"
        self._ensure_model(self.model_path)

        # Initialize MediaPipe HandLandmarker with new API
        base_options = mp.tasks.BaseOptions(
            model_asset_path=str(self.model_path),
            delegate=mp.tasks.BaseOptions.Delegate.CPU,
        )

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.min_detection_confidence,
            min_hand_presence_confidence=self.min_tracking_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )

        self.detector = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.hand_connections = mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS
        self.frame_count = 0
        
        print("✓ Hand Tracker initialized (MediaPipe CPU mode)")
        print(f"  Max hands: {self.max_hands}")
        print(f"  Detection confidence: {self.min_detection_confidence}")
        print(f"  Tracking confidence: {self.min_tracking_confidence}")
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[List[HandDetectionResult]]]:
        """
        Process a frame to detect hands and extract landmarks.
        
        Args:
            frame: Input frame in BGR format (from OpenCV)
        
        Returns:
            Tuple containing:
                - Annotated frame with hand landmarks drawn
                - List of HandDetectionResult (None if no hands detected)
        """
        if frame is None:
            return frame, None
        
        # Increment frame count for timestamp
        self.frame_count += 1
        
        # Convert BGR to RGB (MediaPipe requires RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )
        
        # Process the frame with MediaPipe
        timestamp_ms = self.frame_count * 33  # Approximate 30 FPS
        results = self.detector.detect_for_video(mp_image, timestamp_ms)
        
        # Draw landmarks on the frame
        annotated_frame = frame.copy()
        hand_results = []
        
        if results.hand_landmarks:
            h, w, _ = frame.shape
            
            for idx, hand_landmarks in enumerate(results.hand_landmarks):
                # Draw hand landmarks
                self._draw_landmarks(annotated_frame, hand_landmarks, w, h)
                
                # Extract landmark data
                landmarks = [
                    HandLandmark(lm.x, lm.y, lm.z)
                    for lm in hand_landmarks
                ]
                
                # Get handedness (Left/Right)
                handedness = results.handedness[idx][0]
                hand_label = handedness.category_name
                hand_confidence = handedness.score
                
                # Create result object
                hand_result = HandDetectionResult(
                    landmarks=landmarks,
                    handedness=hand_label,
                    confidence=hand_confidence
                )
                hand_results.append(hand_result)
                
                # Display hand label on frame
                wrist = hand_landmarks[0]  # Wrist landmark
                cv2.putText(
                    annotated_frame,
                    f"{hand_label} ({hand_confidence:.2f})",
                    (int(wrist.x * w), int(wrist.y * h) - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )
        
        return annotated_frame, hand_results if hand_results else None
    
    def _draw_landmarks(self, image: np.ndarray, hand_landmarks, width: int, height: int) -> None:
        """
        Draw hand landmarks and connections on the image.
        
        Args:
            image: Image to draw on
            hand_landmarks: Hand landmark data
            width: Image width
            height: Image height
        """
        # Draw connections
        for connection in self.hand_connections:
            start_idx = connection.start
            end_idx = connection.end
            start_landmark = hand_landmarks[start_idx]
            end_landmark = hand_landmarks[end_idx]
            
            start_point = (int(start_landmark.x * width), int(start_landmark.y * height))
            end_point = (int(end_landmark.x * width), int(end_landmark.y * height))
            
            cv2.line(image, start_point, end_point, (255, 255, 255), 2)
        
        # Draw landmarks
        for landmark in hand_landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            cv2.circle(image, (x, y), 7, (255, 255, 255), 2)
    
    def get_landmark_position(
        self,
        landmarks: List[HandLandmark],
        landmark_id: int,
        frame_width: int,
        frame_height: int
    ) -> Tuple[int, int]:
        """
        Get pixel coordinates of a specific landmark.
        
        Args:
            landmarks: List of hand landmarks
            landmark_id: ID of the landmark (0-20)
            frame_width: Width of the frame in pixels
            frame_height: Height of the frame in pixels
        
        Returns:
            Tuple[int, int]: (x, y) pixel coordinates
        """
        if 0 <= landmark_id < len(landmarks):
            landmark = landmarks[landmark_id]
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            return x, y
        return 0, 0
    
    def calculate_distance(
        self,
        landmarks: List[HandLandmark],
        id1: int,
        id2: int,
        frame_width: int,
        frame_height: int
    ) -> float:
        """
        Calculate Euclidean distance between two landmarks.
        
        Args:
            landmarks: List of hand landmarks
            id1: First landmark ID
            id2: Second landmark ID
            frame_width: Width of the frame in pixels
            frame_height: Height of the frame in pixels
        
        Returns:
            float: Distance in pixels
        """
        x1, y1 = self.get_landmark_position(landmarks, id1, frame_width, frame_height)
        x2, y2 = self.get_landmark_position(landmarks, id2, frame_width, frame_height)
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def release(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, 'detector') and self.detector:
            self.detector.close()
            print("✓ Hand Tracker released")

    def _ensure_model(self, model_path: Path) -> None:
        """Download the hand landmarker model if it does not exist."""
        if model_path.exists():
            return

        model_path.parent.mkdir(parents=True, exist_ok=True)
        url = (
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
            "hand_landmarker/float16/1/hand_landmarker.task"
        )
        print(f"Downloading hand landmarker model to {model_path} ...")
        urlretrieve(url, model_path)
        print("✓ Model downloaded")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - releases resources."""
        self.release()
    
    def __del__(self):
        """Destructor - ensures resources are released."""
        self.release()


# MediaPipe Hand Landmark IDs (for reference)
HAND_LANDMARKS = {
    "WRIST": 0,
    "THUMB_CMC": 1,
    "THUMB_MCP": 2,
    "THUMB_IP": 3,
    "THUMB_TIP": 4,
    "INDEX_FINGER_MCP": 5,
    "INDEX_FINGER_PIP": 6,
    "INDEX_FINGER_DIP": 7,
    "INDEX_FINGER_TIP": 8,
    "MIDDLE_FINGER_MCP": 9,
    "MIDDLE_FINGER_PIP": 10,
    "MIDDLE_FINGER_DIP": 11,
    "MIDDLE_FINGER_TIP": 12,
    "RING_FINGER_MCP": 13,
    "RING_FINGER_PIP": 14,
    "RING_FINGER_DIP": 15,
    "RING_FINGER_TIP": 16,
    "PINKY_MCP": 17,
    "PINKY_PIP": 18,
    "PINKY_DIP": 19,
    "PINKY_TIP": 20,
}
