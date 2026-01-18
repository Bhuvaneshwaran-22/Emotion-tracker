"""
Gesture Vocabulary Engine (Day-3 Core)

This module maps low-level finger states to high-level, context-neutral gesture names.
It is STRICTLY a classification layer - no actions, no OS control, no app logic.

ARCHITECTURAL ROLE:
- Input: finger_states (from gesture_logic.py)
- Output: GestureSignal (symbolic gesture name)
- Responsibility: Pattern matching only, no side effects

DESIGN PRINCIPLES:
1. Deterministic: Same input → same output, always
2. Context-Neutral: Gesture names describe hand shape, not intent
3. Extensible: Easy to add new gestures without breaking existing code
4. Explainable: Rules are simple, readable, interview-friendly

GESTURE NAMING CONVENTION:
- Use VISUAL DESCRIPTORS: "POINT", "FIST", "OPEN_PALM"
- Avoid ACTION WORDS: "SCROLL", "CLICK", "ZOOM" (that's for Day-4)
- Think: "What does the hand look like?" not "What should it do?"
"""

from typing import Dict, Optional
from src.core.gesture_signal import GestureSignal


def identify_gesture(
    finger_states: Dict[str, bool],
    finger_count: int
) -> Optional[GestureSignal]:
    """
    Identify a symbolic gesture from finger states.
    
    This function uses simple, rule-based pattern matching to classify
    hand configurations. It does NOT trigger any actions or side effects.
    
    Args:
        finger_states: Dictionary mapping finger names to UP (True) / DOWN (False)
                      Keys: "thumb", "index", "middle", "ring", "pinky"
        finger_count: Total number of extended fingers (0-5)
    
    Returns:
        GestureSignal object with symbolic name, or None if invalid input
    
    Gesture Vocabulary:
        FIST: All fingers down (0 fingers)
        OPEN_PALM: All fingers up (5 fingers)
        POINT: Only index finger extended
        TWO_FINGERS: Index and middle fingers extended (peace/victory sign)
        UNKNOWN: Any other hand configuration
    
    Example:
        >>> states = {"thumb": False, "index": False, "middle": False, 
        ...           "ring": False, "pinky": False}
        >>> gesture = identify_gesture(states, 0)
        >>> print(gesture.name)
        'FIST'
    """
    # Validate input
    if not finger_states or finger_count < 0 or finger_count > 5:
        return None
    
    # ===== GESTURE CLASSIFICATION RULES =====
    
    # FIST: All fingers down
    if finger_count == 0:
        return GestureSignal(
            name="FIST",
            finger_states=finger_states,
            finger_count=finger_count
        )
    
    # OPEN_PALM: All fingers extended
    if finger_count == 5:
        return GestureSignal(
            name="OPEN_PALM",
            finger_states=finger_states,
            finger_count=finger_count
        )
    
    # POINT: Only index finger up (classic pointing gesture)
    if finger_count == 1 and finger_states.get("index", False):
        return GestureSignal(
            name="POINT",
            finger_states=finger_states,
            finger_count=finger_count
        )
    
    # TWO_FINGERS: Index and middle up (peace sign / victory / number 2)
    if (finger_count == 2 and 
        finger_states.get("index", False) and 
        finger_states.get("middle", False)):
        return GestureSignal(
            name="TWO_FINGERS",
            finger_states=finger_states,
            finger_count=finger_count
        )
    
    # UNKNOWN: Any other configuration
    # This is a SAFE FALLBACK - system never crashes on unexpected input
    return GestureSignal(
        name="UNKNOWN",
        finger_states=finger_states,
        finger_count=finger_count
    )


# ===== FUTURE EXTENSION POINT =====
# When adding new gestures, follow this pattern:
#
# def is_thumbs_up(finger_states: Dict[str, bool]) -> bool:
#     """Helper to detect thumbs up gesture."""
#     return (finger_states.get("thumb", False) and
#             not finger_states.get("index", False) and
#             not finger_states.get("middle", False) and
#             not finger_states.get("ring", False) and
#             not finger_states.get("pinky", False))
#
# Then add to identify_gesture():
#     if finger_count == 1 and is_thumbs_up(finger_states):
#         return GestureSignal(name="THUMBS_UP", ...)
