# DAY-5 QUICK START GUIDE

## 🚀 Running AIRCTRL with Action Execution

### Step 1: Install Dependencies (if not already installed)
```powershell
pip install pyautogui>=0.9.54
```

### Step 2: Run the System
```powershell
python -m src.main
```

### Step 3: Understand the Console Output
```
Right Hand | Gesture: TWO_FINGERS  | Context: BROWSER    | Intent: SCROLL_UP     | Action: scroll_up     | Exec: 🔴 | FPS: 28.5
                │                        │                      │                       │                 │
         Detected Gesture          Active Window          User Intent           Concrete Action    Execution Status
         (from Day-3)              (from Day-4)          (from Day-4)           (from Day-5)       🟢=ON / 🔴=OFF
```

---

## 🎮 Controls

| Key       | Function                          | Effect                                      |
|-----------|-----------------------------------|---------------------------------------------|
| **Q**     | Quit                              | Exit application                            |
| **ESC**   | Quit                              | Exit application                            |
| **S**     | Screenshot                        | Save current frame to screenshots/          |
| **E**     | Toggle Execution                  | Enable/Disable action execution             |

---

## 🛡️ Safety Features

### Default State: DISABLED 🔴
- System starts with execution **OFF**
- Gestures detected → Intents mapped → **Actions BLOCKED**
- Console shows: `🚫 Action blocked (execution disabled): scroll_up`

### Enable Execution: Press 'E'
- System switches to execution **ON**
- Warning message displayed
- Console shows: `🟢 ACTION EXECUTION ENABLED`

### Emergency Stop: Move Mouse to Screen Corner
- Instantly disables ALL actions
- Console shows: `❌ EMERGENCY STOP: Mouse moved to screen corner (FAILSAFE)`
- Execution automatically DISABLED

---

## 📋 Gesture-Action Mapping (Day-5 Scope)

### Browser Context

| Gesture          | Intent        | Action         | OS Operation                |
|------------------|---------------|----------------|-----------------------------|
| TWO_FINGERS      | SCROLL_UP     | scroll_up      | Mouse wheel scroll up       |
| POINT            | SCROLL_DOWN   | scroll_down    | Mouse wheel scroll down     |

### Media Player Context

| Gesture          | Intent        | Action         | OS Operation                |
|------------------|---------------|----------------|-----------------------------|
| TWO_FINGERS      | VOLUME        | volume_up      | System volume increase      |

### Document Context

| Gesture          | Intent        | Action         | OS Operation                |
|------------------|---------------|----------------|-----------------------------|
| TWO_FINGERS      | ZOOM          | zoom_in        | Ctrl + = (zoom in)          |

---

## 🧪 Testing Workflow

### Test 1: Verify Disabled State (Default)
1. Run: `python -m src.main`
2. Make TWO_FINGERS gesture in browser
3. **Expected**: Console shows `🚫 Action blocked`
4. **Expected**: No scrolling occurs

### Test 2: Enable Execution
1. Press `E` key
2. **Expected**: Console shows `🟢 ACTION EXECUTION ENABLED`
3. **Expected**: Warning about real OS operations

### Test 3: Execute Actions
1. Make TWO_FINGERS gesture in browser
2. **Expected**: Console shows `▶️ EXECUTING: scroll_up`
3. **Expected**: Browser page scrolls up

### Test 4: Emergency Stop
1. With execution enabled, move mouse to top-left corner
2. **Expected**: Console shows `❌ EMERGENCY STOP`
3. **Expected**: Execution automatically disabled (🔴)

### Test 5: Disable Execution
1. Press `E` key again
2. **Expected**: Console shows `🔴 ACTION EXECUTION DISABLED`
3. **Expected**: Actions now blocked

---

## 🐛 Troubleshooting

### Issue: Actions not executing
**Solution**: 
- Check execution status: Look for 🟢 (enabled) or 🔴 (disabled)
- Press 'E' to enable execution
- Verify gesture is supported (see mapping table above)

### Issue: Emergency stop triggered accidentally
**Solution**:
- Avoid moving mouse to screen corners during use
- Re-enable execution by pressing 'E'
- Consider disabling failsafe (not recommended for Day-5)

### Issue: Actions execute multiple times
**Solution**:
- Hold gesture steady (don't move hand rapidly)
- Day-6 will implement gesture smoothing
- Current behavior is expected (no temporal filtering yet)

### Issue: Wrong action executed
**Solution**:
- Verify active context (check Console output)
- Ensure correct window is in focus
- Refer to gesture-action mapping table

---

## 📂 File Structure Reference

```
src/
├── main.py                     # Main loop with action pipeline
├── core/
│   ├── action_signal.py        # Immutable action data model
│   ├── action_executor.py      # Safe OS control execution
│   ├── context_signal.py       # Intent data model (Day-4)
│   ├── context_mapper.py       # Intent mapping logic (Day-4)
│   ├── context_detector.py     # Window context detection (Day-4)
│   ├── gesture_signal.py       # Gesture data model (Day-3)
│   ├── gesture_vocabulary.py   # Gesture recognition (Day-3)
│   └── gesture_logic.py        # Finger state detection (Day-2)
├── vision/
│   └── hand_tracker.py         # MediaPipe integration (Day-1)
└── camera/
    └── webcam.py               # Camera capture (Day-1)
```

---

## 🎯 Key Concepts

### Intent vs Action
- **Intent**: Abstract user goal (SCROLL_UP, ZOOM_IN)
- **Action**: Concrete execution method (scroll_up, zoom_in)
- **Separation**: Intent = Domain layer, Action = Infrastructure layer

### Safety-First Design
- **Default Deny**: Execution disabled by default
- **Explicit Enable**: User must opt-in with 'E' key
- **Emergency Stop**: Failsafe always active
- **Transparency**: Every action logged

### Execution Flow
```
Gesture Detection → Context Awareness → Intent Mapping → Action Signal → Execution Gate → OS Control
                                                                              ↑
                                                                     (Enabled/Disabled)
```

---

## 📚 Related Documentation

- **Full Report**: [DAY5_REPORT.md](DAY5_REPORT.md) - Complete architectural details
- **Architecture**: [README.md](README.md) - System overview
- **Installation**: [QUICKSTART.md](QUICKSTART.md) - Setup instructions

---

## ✅ Day-5 Success Criteria

- [x] Action execution is OPTIONAL (disabled by default)
- [x] Toggle execution with 'E' key
- [x] Emergency stop with failsafe
- [x] All actions logged (blocked or executed)
- [x] No system crashes or infinite loops
- [x] OS control isolated to one module
- [x] Clean separation: Intent (what) vs Action (how)

---

**Status**: Day-5 COMPLETE | Safe Action Execution Layer Implemented
**Next**: Day-6 – Gesture Smoothing & Temporal Filtering
