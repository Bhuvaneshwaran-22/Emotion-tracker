"""
Context Mapper Module (Day-4)

This module maps (Gesture + Context) → Intent.
It answers the question: "What does the user WANT to do?"

ARCHITECTURAL ROLE:
- Connects context-neutral gestures with context-specific intents
- Implements the "intelligence" of gesture interpretation
- Remains STRICTLY rule-based (no ML, no training)

DAY-4 SCOPE:
- Map gesture+context combinations to abstract intents
- Intents are DESCRIPTIVE (SCROLL, ZOOM, VOLUME), not IMPERATIVE (scroll(10), zoom(1.5))
- Return ContextSignal objects (immutable, testable)

DAY-5 SCOPE (Future):
- Action Executor will read intent and perform actual OS control
- This layer never touches pyautogui, pynput, or OS APIs

DESIGN PHILOSOPHY:
- Rules over heuristics (deterministic, explainable)
- Extensible (easy to add new gesture→intent mappings)
- Fail-safe (unknown combinations → intent=NONE)

INTERVIEW TALKING POINTS:
- Why rule-based? Predictable, debuggable, no training data needed
- Why abstract intents? Decouples "what" from "how" (Day-4 vs Day-5)
- Why ContextSignal? Immutable, traceable, testable
"""

from typing import Optional
from src.core.gesture_signal import GestureSignal
from src.core.context_signal import ContextSignal


# ===== INTENT MAPPING RULES =====
# Maps (gesture_name, context_name) → intent_name
#
# Structure:
#   INTENT_RULES = {
#       "GESTURE_NAME": {
#           "CONTEXT_NAME": "INTENT_NAME",
#           ...
#       },
#       ...
#   }
#
# Design Rationale:
#   - Flat, readable structure (easy to understand in interviews)
#   - Easy to extend (add new gestures or contexts)
#   - Deterministic (no ambiguity or probability)

INTENT_RULES = {
    # FIST gesture: Stop/pause actions
    "FIST": {
        "BROWSER": "PAUSE",      # Pause video/animation
        "MEDIA": "PAUSE",         # Pause playback
        "IDE": "NONE",            # No action in IDE
        "UNKNOWN": "NONE",        # Default: no intent
    },
    
    # OPEN_PALM gesture: Reset/home actions
    "OPEN_PALM": {
        "BROWSER": "HOME",        # Scroll to top / go home
        "MEDIA": "STOP",          # Stop playback
        "DOCUMENT": "FIT_PAGE",   # Fit page to window
        "UNKNOWN": "NONE",
    },
    
    # POINT gesture: Navigate/select
    "POINT": {
        "BROWSER": "SCROLL_DOWN",  # Scroll down while pointing
        "DOCUMENT": "SCROLL_DOWN",
        "MEDIA": "SEEK_FORWARD",   # Seek forward in video
        "IDE": "NEXT_LINE",        # Navigate to next line
        "EXPLORER": "NAVIGATE",    # Navigate through files
        "UNKNOWN": "NONE",
    },
    
    # TWO_FINGERS gesture: Zoom/volume control
    "TWO_FINGERS": {
        "BROWSER": "SCROLL_UP",    # Scroll up with two fingers
        "DOCUMENT": "ZOOM",        # Zoom in/out PDF
        "MEDIA": "VOLUME",         # Volume control
        "IDE": "ZOOM",             # Zoom in/out code
        "UNKNOWN": "NONE",
    },
    
    # UNKNOWN gesture: No intent (fallback)
    "UNKNOWN": {
        "BROWSER": "NONE",
        "MEDIA": "NONE",
        "IDE": "NONE",
        "UNKNOWN": "NONE",
    },
}


def map_gesture_to_intent(
    gesture_signal: Optional[GestureSignal],
    context_name: str
) -> ContextSignal:
    """
    Map a gesture in a specific context to a user intent.
    
    This is the CORE LOGIC of context-aware gesture interpretation.
    It uses simple rule matching to determine what the user wants to do.
    
    Args:
        gesture_signal: The recognized gesture (from vocabulary engine)
        context_name: The detected context (from context detector)
    
    Returns:
        ContextSignal: Immutable object representing the inferred intent
    
    Design Philosophy:
        - INTENT is NOT ACTION
        - "SCROLL" means "user wants to scroll", not "execute scroll()"
        - Day-5 will read this intent and decide HOW to execute it
    
    Example Flow:
        Input: GestureSignal("TWO_FINGERS"), Context("BROWSER")
        Output: ContextSignal(gesture="TWO_FINGERS", context="BROWSER", intent="SCROLL_UP")
        
        Day-5 will then:
        - Read intent="SCROLL_UP"
        - Execute: pyautogui.scroll(5)  # ← NOT done here!
    
    Error Handling:
        - If gesture is None → return ContextSignal with intent="NONE"
        - If no rule exists → return ContextSignal with intent="NONE"
        - Never crashes, always returns valid ContextSignal
    """
    # Handle invalid gesture input
    if gesture_signal is None:
        return ContextSignal(
            gesture_name="INVALID",
            context_name=context_name,
            intent_name="NONE"
        )
    
    gesture_name = gesture_signal.name
    
    # Lookup intent from mapping rules
    # Use nested .get() for safe dictionary access
    gesture_rules = INTENT_RULES.get(gesture_name, {})
    intent_name = gesture_rules.get(context_name, "NONE")
    
    # If no exact context match, try fallback to UNKNOWN
    if intent_name == "NONE" and context_name != "UNKNOWN":
        intent_name = gesture_rules.get("UNKNOWN", "NONE")
    
    # Construct and return immutable ContextSignal
    return ContextSignal(
        gesture_name=gesture_name,
        context_name=context_name,
        intent_name=intent_name
    )


# ===== UTILITY FUNCTIONS (Future) =====

def get_all_supported_contexts() -> list[str]:
    """
    Get list of all contexts that have gesture mappings.
    Useful for debugging and system introspection.
    """
    contexts = set()
    for gesture_rules in INTENT_RULES.values():
        contexts.update(gesture_rules.keys())
    return sorted(contexts)


def get_gestures_for_context(context_name: str) -> dict[str, str]:
    """
    Get all gesture→intent mappings for a specific context.
    Useful for generating help screens or documentation.
    
    Example:
        >>> get_gestures_for_context("BROWSER")
        {
            "FIST": "PAUSE",
            "OPEN_PALM": "HOME",
            "POINT": "SCROLL_DOWN",
            "TWO_FINGERS": "SCROLL_UP"
        }
    """
    mappings = {}
    for gesture_name, gesture_rules in INTENT_RULES.items():
        if context_name in gesture_rules:
            intent = gesture_rules[context_name]
            if intent != "NONE":
                mappings[gesture_name] = intent
    return mappings


# ===== EXTENSION GUIDE =====
#
# HOW TO ADD NEW GESTURE→INTENT MAPPINGS:
#
# 1. Add gesture to gesture_vocabulary.py (Day-3)
#    Example: "THUMBS_UP" gesture
#
# 2. Add rules to INTENT_RULES in this file
#    INTENT_RULES["THUMBS_UP"] = {
#        "BROWSER": "LIKE",
#        "MEDIA": "PLAY",
#        "UNKNOWN": "NONE"
#    }
#
# 3. (Day-5) Add intent→action mapping in action_executor.py
#    if intent == "LIKE":
#        # Simulate clicking like button
#        pyautogui.click()
#
# THAT'S IT! No changes needed in main.py or other modules.
# This is clean, modular architecture.
