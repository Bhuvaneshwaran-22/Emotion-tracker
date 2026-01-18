"""
Webcam Module - Handles webcam initialization and frame capture.

This module provides a clean abstraction for webcam operations,
making it easy to capture frames with error handling and resource management.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class Webcam:
    """
    Webcam abstraction class for capturing video frames.
    
    Attributes:
        camera_index (int): Index of the camera device (default: 0)
        width (int): Frame width in pixels
        height (int): Frame height in pixels
        fps (int): Target frames per second
    """
    
    def __init__(
        self,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30
    ):
        """
        Initialize the webcam with specified parameters.
        
        Args:
            camera_index: Camera device index (0 for default webcam)
            width: Desired frame width
            height: Desired frame height
            fps: Target frames per second
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False
    
    def start(self) -> bool:
        """
        Start the webcam capture.
        
        Returns:
            bool: True if webcam started successfully, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.is_opened = True
            print(f"✓ Webcam started successfully (Camera {self.camera_index})")
            print(f"  Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            print(f"  FPS: {int(self.cap.get(cv2.CAP_PROP_FPS))}")
            return True
            
        except Exception as e:
            print(f"Error starting webcam: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a single frame from the webcam.
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]: 
                - Success flag (True if frame captured successfully)
                - Frame as numpy array (BGR format) or None if failed
        """
        if not self.is_opened or self.cap is None:
            return False, None
        
        success, frame = self.cap.read()
        
        if not success:
            print("Warning: Failed to capture frame")
            return False, None
        
        return True, frame
    
    def release(self) -> None:
        """
        Release the webcam resource and clean up.
        """
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            print("✓ Webcam released")
    
    def __enter__(self):
        """Context manager entry - starts the webcam."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - releases the webcam."""
        self.release()
    
    def __del__(self):
        """Destructor - ensures webcam is released."""
        self.release()
