"""
Action Signal Data Model (Day-5)

This module defines the data structure for executable system actions.
It represents CONCRETE EXECUTION — not abstract intent.

ARCHITECTURAL ROLE:
- Converts abstract intent (SCROLL, ZOOM, VOLUME) into actionable commands
- Bridges the gap between "what user wants" and "what system does"
- Separates intent semantics from execution mechanics

DAY-5 SCOPE:
- Represent the final executable action derived from user intent
- Action is concrete (scroll_up, volume_up, zoom_in) not abstract
- No OS control logic here — just a data carrier

DESIGN PHILOSOPHY:
- Intent describes MEANING → Action describes EXECUTION
- Intent is context-aware → Action is context-agnostic
- Intent is strategic → Action is tactical

Example Flow:
    ContextSignal(intent="SCROLL_UP")
    → Action Executor analyzes intent
    → ActionSignal(intent_name="SCROLL_UP", action_name="scroll_up")
    → Action Executor executes: pyautogui.scroll(5)

Interview Talking Points:
- Why separate ActionSignal from ContextSignal?
  → Intent is "what" (domain layer), Action is "how" (infrastructure layer)
  → Intent can map to multiple actions depending on execution strategy
  → Action is the last immutable checkpoint before OS control
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionSignal:
    """
    Immutable representation of a concrete system action.
    
    This represents HOW to execute user intent, not WHAT the user wants.
    The action is derived from intent but remains execution-focused.
    
    Attributes:
        intent_name: The abstract intent from ContextSignal (e.g., "SCROLL_UP")
        action_name: The concrete action to execute (e.g., "scroll_up")
    
    Design Philosophy:
        - INTENT = MEANING, ACTION = EXECUTION
        - Intent is high-level, Action is low-level
        - One intent can map to multiple actions (future expansion)
        
    Example Mappings:
        Intent "SCROLL_UP" → Action "scroll_up" → pyautogui.scroll(5)
        Intent "VOLUME_UP" → Action "volume_up" → pyautogui.press('volumeup')
        Intent "ZOOM_IN" → Action "zoom_in" → pyautogui.hotkey('ctrl', '+')
        Intent "NONE" → Action "no_action" → (do nothing)
    
    Design Notes:
        - frozen=True ensures immutability (thread-safe, predictable)
        - Action names use snake_case (convention for function-like operations)
        - Intent names use UPPER_CASE (convention for constants/enums)
        - This dual naming clarifies the semantic shift: INTENT → action
    
    Safety Design:
        - ActionSignal itself performs NO execution
        - It's a pure data carrier (safe to create, log, inspect)
        - Execution is delegated to ActionExecutor (controlled, optional)
    """
    intent_name: str
    action_name: str
    
    def __repr__(self) -> str:
        """
        Custom string representation for debugging and logging.
        
        Returns:
            Human-readable string showing intent → action mapping
        """
        return f"ActionSignal(intent='{self.intent_name}' → action='{self.action_name}')"
