"""
Context Detector Module (Day-4)

This module detects the currently active application context on Windows.
It answers the question: "Where is the user's attention?"

ARCHITECTURAL ROLE:
- Provides environmental awareness to the gesture system
- Enables context-sensitive gesture interpretation
- Remains lightweight and CPU-safe (no polling loops here)

DAY-4 SCOPE:
- Detect active window/application name on Windows
- Return standardized context names
- Handle failures gracefully (return "UNKNOWN")

DESIGN PHILOSOPHY:
- Use Windows API via ctypes (no heavy dependencies)
- Keep detection logic simple and fast
- Normalize app names to standard categories (Chrome → Browser)

INTERVIEW TALKING POINTS:
- Why ctypes? Lightweight, built-in, no external dependencies
- Why normalize? Same intent across similar apps (Chrome/Edge/Firefox = Browser)
- Why "UNKNOWN" fallback? System never crashes on detection failure
"""

import ctypes
from ctypes import wintypes
import re


# ===== WINDOWS API DECLARATIONS =====
# Using ctypes to access Windows API without external dependencies

try:
    # Get handle to foreground window
    user32 = ctypes.windll.user32
    
    # Function signatures for Windows API calls
    user32.GetForegroundWindow.argtypes = []
    user32.GetForegroundWindow.restype = wintypes.HWND
    
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    
    WINDOWS_API_AVAILABLE = True
    
except Exception:
    # If Windows API is unavailable (non-Windows platform), disable context detection
    WINDOWS_API_AVAILABLE = False


# ===== CONTEXT CATEGORY MAPPINGS =====
# Maps application names to standardized context categories

CONTEXT_MAPPINGS = {
    # Web Browsers
    r"chrome|edge|firefox|brave|opera|safari": "BROWSER",
    
    # Media Players
    r"vlc|spotify|youtube|netflix|media player|groove": "MEDIA",
    
    # IDEs and Code Editors
    r"visual studio code|vscode|pycharm|intellij|sublime|atom|notepad\+\+": "IDE",
    
    # Office Applications
    r"word|excel|powerpoint|outlook|onenote": "OFFICE",
    
    # PDF Readers
    r"acrobat|pdf|foxit|sumatra": "DOCUMENT",
    
    # File Explorers
    r"explorer|file explorer": "EXPLORER",
}


def get_active_window_title() -> str:
    """
    Get the title of the currently active (foreground) window on Windows.
    
    Uses Windows API via ctypes to retrieve the window title.
    This is a low-level, lightweight operation with minimal CPU overhead.
    
    Returns:
        str: Window title, or empty string if detection fails
    
    Technical Notes:
        - GetForegroundWindow(): Returns handle to active window
        - GetWindowTextW(): Retrieves window title as Unicode string
        - Error handling prevents crashes on API failures
    """
    if not WINDOWS_API_AVAILABLE:
        return ""
    
    try:
        # Get handle to the foreground window
        hwnd = user32.GetForegroundWindow()
        
        if not hwnd:
            return ""
        
        # Get the length of the window title
        length = user32.GetWindowTextLengthW(hwnd)
        
        if length == 0:
            return ""
        
        # Allocate buffer and retrieve window title
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        
        return buffer.value
    
    except Exception:
        # Silently fail - context detection is non-critical
        return ""


def normalize_context(window_title: str) -> str:
    """
    Normalize a window title to a standardized context category.
    
    This function maps specific application names to generic categories,
    allowing the same gesture to work across similar applications.
    
    Args:
        window_title: Raw window title from get_active_window_title()
    
    Returns:
        str: Standardized context name (BROWSER, MEDIA, IDE, etc.) or "UNKNOWN"
    
    Design Rationale:
        - User doesn't care if they're in Chrome or Firefox - both are browsers
        - Intent mapping becomes simpler (one rule for "BROWSER" vs. many for each browser)
        - Easy to extend with new categories without changing intent logic
    
    Example:
        >>> normalize_context("Google Chrome - Stack Overflow")
        'BROWSER'
        >>> normalize_context("Spotify")
        'MEDIA'
    """
    if not window_title:
        return "UNKNOWN"
    
    # Convert to lowercase for case-insensitive matching
    title_lower = window_title.lower()
    
    # Check each category's regex pattern
    for pattern, category in CONTEXT_MAPPINGS.items():
        if re.search(pattern, title_lower):
            return category
    
    # If no match found, return the raw title (truncated for readability)
    # This allows for manual debugging and future rule additions
    return "UNKNOWN"


def get_active_context() -> str:
    """
    Detect and return the current application context.
    
    This is the main entry point for context detection.
    It combines window title retrieval and normalization into one call.
    
    Returns:
        str: Standardized context name (BROWSER, MEDIA, IDE, UNKNOWN, etc.)
    
    Usage in main loop:
        >>> context = get_active_context()
        >>> print(f"User is in: {context}")
        User is in: BROWSER
    
    Performance:
        - Single Windows API call (GetForegroundWindow + GetWindowText)
        - Regex matching on short string (~10-100 chars)
        - Total overhead: < 1ms per call
        - Safe to call every frame (30-60 FPS)
    
    Error Handling:
        - Returns "UNKNOWN" if detection fails
        - Never crashes or blocks the main loop
        - Silently degrades to context-unaware mode
    """
    window_title = get_active_window_title()
    return normalize_context(window_title)


# ===== EXTENSION POINT FOR FUTURE =====
# To add new context categories:
# 1. Add pattern to CONTEXT_MAPPINGS dictionary
# 2. Update context_mapper.py with intent rules for new context
# 3. No changes needed here or in main.py
#
# Example:
# CONTEXT_MAPPINGS[r"discord|slack|teams|zoom"] = "COMMUNICATION"
