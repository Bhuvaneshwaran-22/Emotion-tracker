"""
Gesture Signal Data Model

This module defines an immutable data structure representing a recognized gesture.
It is a SYMBOLIC, CONTEXT-NEUTRAL representation of a hand configuration.

ARCHITECTURAL PURPOSE:
- Decouples "what the hand looks like" from "what action to take"
- Provides a stable interface between gesture vocabulary and future context layers
- Makes the system testable, explainable, and maintainable

DAY-3 SCOPE:
- Immutable gesture representation
- No action logic, no OS control, no app-specific meaning

FUTURE USE (Day-4+):
- Context layer will map GestureSignal → Actions based on application state
- Example: POINT gesture could mean "scroll" in browser, "next slide" in presentation
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class GestureSignal:
    """
    Immutable representation of a recognized hand gesture.
    
    This is a SYMBOLIC DESCRIPTION only - it carries no behavioral logic.
    The name describes the hand's visual configuration, not its meaning.
    
    Attributes:
        name: Human-readable gesture identifier (e.g., "POINT", "FIST", "OPEN_PALM")
        finger_states: Raw finger up/down state that generated this signal
        finger_count: Number of extended fingers (0-5)
    
    Design Notes:
        - frozen=True ensures immutability (thread-safe, hashable, predictable)
        - Gesture names are DESCRIPTIVE, not PRESCRIPTIVE
        - This object should never contain action logic or side effects
    """
    
    name: str
    finger_states: Dict[str, bool]
    finger_count: int
    
    def __repr__(self) -> str:
        """Clean string representation for debugging and logging."""
        return f"GestureSignal(name='{self.name}', finger_count={self.finger_count})"
