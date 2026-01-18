"""
Action Executor Module (Day-5)

This module executes concrete system actions derived from user intents.
It is the ONLY module with OS-level control permissions.

ARCHITECTURAL ROLE:
- Translates abstract intents into concrete OS operations
- Enforces safety controls (enable/disable, failsafe, logging)
- Isolates all pyautogui/pynput logic in ONE place

DAY-5 SCOPE:
- Execute actions ONLY when explicitly enabled
- Support basic intents: SCROLL, VOLUME, ZOOM, NONE
- Use pyautogui with failsafe mode enabled
- Log every action attempt (executed or blocked)

SAFETY RULES (CRITICAL):
- Global execution flag (default: DISABLED)
- No execution unless explicitly enabled
- Failsafe: moving mouse to corner stops all actions
- No infinite loops or background threads
- Print every action for transparency

DESIGN PHILOSOPHY:
- Safety first: better to do nothing than something wrong
- Explicit over implicit: execution is opt-in, not default
- Reversible: toggle execution without restarting system
- Observable: every action is logged

Interview Talking Points:
- Why isolate in one module? Single responsibility, easy to remove/replace
- Why global flag? One control point prevents race conditions
- Why print actions? Transparency builds trust, aids debugging
- Why pyautogui? Cross-platform, simple API, built-in safety
"""

import pyautogui
from typing import Optional
from src.core.action_signal import ActionSignal
from src.core.context_signal import ContextSignal


# ===== GLOBAL EXECUTION STATE =====
# CRITICAL: This flag controls ALL action execution
# Default: DISABLED (safe-by-default principle)
_execution_enabled: bool = False

# Configure pyautogui safety features
# FAILSAFE: Moving mouse to screen corner raises FailSafeException
pyautogui.FAILSAFE = True

# PAUSE: Delay between pyautogui actions (prevents rapid-fire)
pyautogui.PAUSE = 0.1  # 100ms delay between actions


def enable_execution() -> None:
    """
    Enable action execution globally.
    
    After calling this function, execute_action() will perform real OS operations.
    Use with caution — ensures user has explicitly opted in to system control.
    
    Safety Note:
        - Execution should only be enabled after user confirmation
        - Can be disabled at any time with disable_execution()
    """
    global _execution_enabled
    _execution_enabled = True
    print("\n🟢 ACTION EXECUTION ENABLED")
    print("   ⚠️  System will now perform real OS operations")
    print("   ⚠️  Move mouse to screen corner to emergency stop (FAILSAFE)")


def disable_execution() -> None:
    """
    Disable action execution globally.
    
    After calling this function, execute_action() will block all operations.
    Safe default state — system observes but does not act.
    
    Safety Note:
        - This is the DEFAULT state (safe-by-default)
        - Can be re-enabled with enable_execution()
    """
    global _execution_enabled
    _execution_enabled = False
    print("\n🔴 ACTION EXECUTION DISABLED")
    print("   ✓ System will observe intents but perform no OS operations")


def is_execution_enabled() -> bool:
    """
    Check if action execution is currently enabled.
    
    Returns:
        True if execution is enabled, False otherwise
    """
    return _execution_enabled


def intent_to_action(context_signal: ContextSignal) -> ActionSignal:
    """
    Convert abstract intent to concrete action.
    
    This function maps high-level user intent (from ContextSignal)
    to low-level system action (ActionSignal).
    
    Args:
        context_signal: The context-aware intent signal
    
    Returns:
        ActionSignal: The executable action specification
    
    Design Philosophy:
        - Intent is "what user wants" (domain layer)
        - Action is "how to execute" (infrastructure layer)
        - This mapping is the translation boundary
    
    Supported Intent → Action Mappings:
        SCROLL_UP    → scroll_up
        SCROLL_DOWN  → scroll_down
        VOLUME_UP    → volume_up
        VOLUME_DOWN  → volume_down
        ZOOM_IN      → zoom_in
        ZOOM_OUT     → zoom_out
        NONE         → no_action
        (unknown)    → no_action
    """
    intent_name = context_signal.intent_name
    
    # Map intent to action name
    # For Day-5, we use simple 1:1 mapping (future: complex strategies)
    intent_to_action_map = {
        "SCROLL_UP": "scroll_up",
        "SCROLL_DOWN": "scroll_down",
        "VOLUME": "volume_up",  # Default volume action (up)
        "VOLUME_UP": "volume_up",
        "VOLUME_DOWN": "volume_down",
        "ZOOM": "zoom_in",  # Default zoom action (in)
        "ZOOM_IN": "zoom_in",
        "ZOOM_OUT": "zoom_out",
        "PAUSE": "no_action",  # Day-5: not implemented yet
        "HOME": "no_action",   # Day-5: not implemented yet
        "NONE": "no_action",
    }
    
    action_name = intent_to_action_map.get(intent_name, "no_action")
    
    return ActionSignal(
        intent_name=intent_name,
        action_name=action_name
    )


def execute_action(action_signal: ActionSignal) -> None:
    """
    Execute a system action (if execution is enabled).
    
    This is the ONLY function that performs actual OS operations.
    All safety checks are enforced here.
    
    Args:
        action_signal: The action to execute
    
    Safety Guarantees:
        - No execution if _execution_enabled is False
        - All actions are logged (executed or blocked)
        - pyautogui.FAILSAFE is always enabled
        - Unknown actions are ignored (fail-safe)
    
    Execution Flow:
        1. Check global execution flag
        2. If disabled → log and return
        3. If enabled → log and execute via pyautogui
        4. If action unknown → log and return
    
    Error Handling:
        - pyautogui.FailSafeException: Mouse moved to corner (emergency stop)
        - Unknown action: Logged and ignored (no crash)
    """
    # Safety Check #1: Verify execution is enabled
    if not _execution_enabled:
        print(f"   🚫 Action blocked (execution disabled): {action_signal.action_name}")
        return
    
    # Safety Check #2: Ignore no_action
    if action_signal.action_name == "no_action":
        print(f"   ⚪ No action required (intent: {action_signal.intent_name})")
        return
    
    # Log the action we're about to execute
    print(f"   ▶️  EXECUTING: {action_signal.action_name} (intent: {action_signal.intent_name})")
    
    # Execute the action using pyautogui
    try:
        if action_signal.action_name == "scroll_up":
            pyautogui.scroll(5)  # Scroll up (positive = up)
        
        elif action_signal.action_name == "scroll_down":
            pyautogui.scroll(-5)  # Scroll down (negative = down)
        
        elif action_signal.action_name == "volume_up":
            pyautogui.press('volumeup')
        
        elif action_signal.action_name == "volume_down":
            pyautogui.press('volumedown')
        
        elif action_signal.action_name == "zoom_in":
            pyautogui.hotkey('ctrl', '=')  # Ctrl + = (zoom in)
        
        elif action_signal.action_name == "zoom_out":
            pyautogui.hotkey('ctrl', '-')  # Ctrl + - (zoom out)
        
        else:
            # Unknown action — log and ignore (fail-safe)
            print(f"   ⚠️  Unknown action '{action_signal.action_name}' — ignoring")
    
    except pyautogui.FailSafeException:
        # User moved mouse to corner — emergency stop
        print("\n\n❌ EMERGENCY STOP: Mouse moved to screen corner (FAILSAFE)")
        print("   Disabling execution for safety...")
        disable_execution()
    
    except Exception as e:
        # Unexpected error — log but don't crash
        print(f"   ❌ Error executing action '{action_signal.action_name}': {e}")


# ===== MODULE INITIALIZATION =====
# Print safety status on module load
print(f"Action Executor loaded | Execution: {'ENABLED' if _execution_enabled else 'DISABLED'} | Failsafe: ON")
