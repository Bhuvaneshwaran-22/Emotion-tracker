"""
Context Signal Data Model (Day-4)

This module defines the data structure for context-aware gesture interpretation.
It represents USER INTENT — not system actions.

ARCHITECTURAL ROLE:
- Bridges the gap between context-neutral gestures and action execution
- Answers the question: "What does the user WANT to do?"
- Does NOT answer: "How should the system DO it?"

DAY-4 SCOPE:
- Represent the combination of gesture + context → intent
- Intent is abstract (SCROLL, ZOOM, VOLUME) not concrete (move mouse, press key)
- No action logic, no OS control, no side effects

DAY-5 SCOPE (Future):
- Action Executor will read ContextSignal and perform actual OS control
- Example: ContextSignal(intent="SCROLL") → pyautogui.scroll()
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextSignal:
    """
    Immutable representation of user intent in a specific context.
    
    This represents WHAT the user wants, not HOW to execute it.
    The intent is context-aware but remains abstract.
    
    Attributes:
        gesture_name: The recognized gesture (from GestureSignal)
        context_name: The detected application/window context
        intent_name: The inferred user intent (abstract action)
    
    Design Philosophy:
        - INTENT ≠ ACTION
        - "SCROLL" is an intent, "pyautogui.scroll()" is an action
        - This layer decides WHAT, Day-5 decides HOW
        
    Example Flow:
        GestureSignal("TWO_FINGERS") + Context("Chrome")
        → ContextSignal(gesture="TWO_FINGERS", context="Chrome", intent="SCROLL")
        → (Day-5) Action Executor scrolls the page
    
    Design Notes:
        - frozen=True ensures immutability (predictable, thread-safe)
        - Intent names are ABSTRACT (SCROLL, ZOOM, VOLUME, NONE)
        - This keeps the architecture clean and testable
    """
    
    gesture_name: str
    context_name: str
    intent_name: str
    
    def __repr__(self) -> str:
        """Clean string representation for debugging and logging."""
        return (f"ContextSignal(gesture='{self.gesture_name}', "
                f"context='{self.context_name}', intent='{self.intent_name}')")
    
    def has_intent(self) -> bool:
        """Check if this signal represents a meaningful intent."""
        return self.intent_name != "NONE" and self.intent_name != "UNKNOWN"
