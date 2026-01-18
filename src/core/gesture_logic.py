"""
Gesture Logic Module - Finger State Detection (Day-2 Scope)

This module is STRICTLY focused on detecting finger states from hand landmarks.
No gesture meanings, no hard-coded actions, no future assumptions.

DAY-2 SCOPE:
- Detect which fingers are UP or DOWN
- Count extended fingers
- Return symbolic hand state

DAY-3 SCOPE (NOT HERE):
- Map states to gesture meanings
- Handle context-aware mappings
- Trigger system actions

DESIGN PRINCIPLE:
Decouple detection from meaning. This allows Day-3 to map the same 
hand state to different meanings based on context.
"""

from typing import Dict, List, Tuple


# ===== LANDMARK INDEX CONSTANTS =====
# MediaPipe Hands provides 21 landmarks per hand
# Reference: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker

class LANDMARKS:
    """Hand landmark indices for coordinate access."""
    WRIST = 0
    
    # Thumb
    THUMB_TIP = 4
    THUMB_MCP = 2
    
    # Index
    INDEX_TIP = 8
    INDEX_PIP = 6
    
    # Middle
    MIDDLE_TIP = 12
    MIDDLE_PIP = 10
    
    # Ring
    RING_TIP = 16
    RING_PIP = 14
    
    # Pinky
    PINKY_TIP = 20
    PINKY_PIP = 18


# ===== CORE DETECTION FUNCTIONS =====

def get_finger_states(landmarks: List[Tuple[float, float]]) -> Dict[str, bool]:
    """
    Detect finger UP/DOWN state from hand landmarks.
    
    DETECTION LOGIC (No meaning attached):
    - Regular fingers: tip_y < pip_y means UP (lower Y = higher on screen)
    - Thumb: tip_x distance from mcp_x determines if extended
    
    Args:
        landmarks: List of 21 (x, y) coordinate tuples, normalized [0.0, 1.0]
    
    Returns:
        Dictionary: {"thumb": bool, "index": bool, "middle": bool, "ring": bool, "pinky": bool}
    
    Raises:
        ValueError: If landmarks length != 21
    """
    if len(landmarks) != 21:
        raise ValueError(f"Expected 21 landmarks, got {len(landmarks)}")
    
    finger_states = {}
    
    # ===== THUMB =====
    # Thumb moves horizontally - detect extension by X-axis distance
    thumb_tip_x = landmarks[LANDMARKS.THUMB_TIP][0]
    thumb_mcp_x = landmarks[LANDMARKS.THUMB_MCP][0]
    thumb_distance = abs(thumb_tip_x - thumb_mcp_x)
    finger_states["thumb"] = thumb_distance > 0.05
    
    # ===== INDEX FINGER =====
    # Detect if tip is above PIP joint
    index_tip_y = landmarks[LANDMARKS.INDEX_TIP][1]
    index_pip_y = landmarks[LANDMARKS.INDEX_PIP][1]
    finger_states["index"] = index_tip_y < index_pip_y
    
    # ===== MIDDLE FINGER =====
    middle_tip_y = landmarks[LANDMARKS.MIDDLE_TIP][1]
    middle_pip_y = landmarks[LANDMARKS.MIDDLE_PIP][1]
    finger_states["middle"] = middle_tip_y < middle_pip_y
    
    # ===== RING FINGER =====
    ring_tip_y = landmarks[LANDMARKS.RING_TIP][1]
    ring_pip_y = landmarks[LANDMARKS.RING_PIP][1]
    finger_states["ring"] = ring_tip_y < ring_pip_y
    
    # ===== PINKY =====
    pinky_tip_y = landmarks[LANDMARKS.PINKY_TIP][1]
    pinky_pip_y = landmarks[LANDMARKS.PINKY_PIP][1]
    finger_states["pinky"] = pinky_tip_y < pinky_pip_y
    
    return finger_states


def count_fingers_up(finger_states: Dict[str, bool]) -> int:
    """
    Count how many fingers are currently extended.
    
    Args:
        finger_states: Dictionary from get_finger_states()
    
    Returns:
        Integer: 0–5 (number of extended fingers)
    """
    return sum(1 for state in finger_states.values() if state)
