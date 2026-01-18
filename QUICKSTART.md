# AIRCTRL - Quick Start Guide

## ✅ Environment Setup Complete!

Your AIRCTRL project is ready to run. Here's what has been set up:

### 📦 Installed Packages
- ✅ OpenCV 4.11.0 (Computer Vision)
- ✅ MediaPipe 0.10.31 (Hand Tracking)
- ✅ NumPy 2.4.1 (Numerical Computing)

### 🗂️ Project Structure Created
```
AIRCTRL/
├── src/
│   ├── camera/
│   │   ├── __init__.py
│   │   └── webcam.py          ✅ Webcam abstraction (59 lines)
│   ├── vision/
│   │   ├── __init__.py
│   │   └── hand_tracker.py    ✅ Hand tracking (227 lines)
│   ├── core/
│   │   └── __init__.py        ✅ Reserved for expansion
│   ├── __init__.py
│   └── main.py                ✅ Entry point (146 lines)
├── .vscode/
│   ├── launch.json            ✅ Debug configuration
│   └── settings.json          ✅ VS Code settings
├── requirements.txt           ✅ Dependencies list
├── README.md                  ✅ Full documentation
├── .gitignore                 ✅ Git ignore rules
└── .venv/                     ✅ Virtual environment
```

---

## 🚀 How to Run (3 Methods)

### Method 1: Using Python Module (RECOMMENDED)
```powershell
python -m src.main
```

### Method 2: Using VS Code Debugger
1. Press **F5** or go to **Run and Debug** (Ctrl+Shift+D)
2. Select **"AIRCTRL: Run Main"** from the dropdown
3. Click the green play button

### Method 3: Using Terminal
```powershell
cd "d:\My-Projects\Air control"
& ".\.venv\Scripts\python.exe" -m src.main
```

---

## 🎮 Application Controls

While running:
- **Q** or **ESC** → Quit
- **S** → Save screenshot (saved to `screenshots/` folder)

---

## 📊 What to Expect

When you run the application:
1. Console will show initialization messages
2. Webcam will start (you'll see a light indicator on your camera)
3. A window titled "AIRCTRL - Hand Tracking" will open
4. Show your hand to the camera
5. You'll see:
   - 21 green landmarks on your hand
   - Connections between landmarks (skeleton)
   - Hand label ("Left" or "Right")
   - Confidence score
   - Real-time FPS counter

---

## 🔧 Troubleshooting

### Issue: "Could not open camera 0"
**Solutions:**
1. Close other apps using the webcam (Teams, Zoom, Discord)
2. Grant camera permissions:
   - Windows Settings → Privacy → Camera → Allow apps to access camera
3. Try a different camera index in [main.py](src/main.py):
   ```python
   webcam = Webcam(camera_index=1)  # Try 1 or 2
   ```

### Issue: Import Errors
**Solution:**
Always run from the project root using:
```powershell
python -m src.main
```

### Issue: Low FPS / Laggy Performance
**Solutions:**
1. Lower resolution in [main.py](src/main.py):
   ```python
   webcam = Webcam(width=640, height=480)
   ```
2. Close other resource-intensive applications
3. Ensure you're using `model_complexity=0` (already set)

### Issue: Hand Not Detected
**Solutions:**
1. Ensure good lighting
2. Show palm clearly to camera
3. Keep hand within frame
4. Lower `min_detection_confidence` in [main.py](src/main.py):
   ```python
   hand_tracker = HandTracker(min_detection_confidence=0.5)
   ```

---

## 🎯 Next Steps

### 1. Test the Basic Demo
Run the application and verify hand tracking works:
```powershell
python -m src.main
```

### 2. Explore the Code
- **[src/camera/webcam.py](src/camera/webcam.py)** - Learn webcam operations
- **[src/vision/hand_tracker.py](src/vision/hand_tracker.py)** - Understand hand tracking
- **[src/main.py](src/main.py)** - See how components work together

### 3. Experiment
Try modifying:
- Webcam resolution (line 31 in main.py)
- Detection confidence (line 37 in main.py)
- Max hands (line 36 in main.py - set to 2 for both hands)

### 4. Build Gestures
Add custom gesture detection in [src/core/](src/core/):
- Pinch detection (thumb + index finger distance)
- Fist detection (all fingers closed)
- Peace sign (2 fingers up)
- Swipe gestures (hand movement tracking)

---

## 📚 Code Examples

### Example 1: Get Finger Positions
```python
if hand_results:
    hand = hand_results[0]
    landmarks = hand.landmarks
    h, w, _ = frame.shape
    
    # Get index finger tip position
    index_tip = tracker.get_landmark_position(landmarks, 8, w, h)
    print(f"Index finger at: {index_tip}")
```

### Example 2: Detect Pinch Gesture
```python
if hand_results:
    hand = hand_results[0]
    h, w, _ = frame.shape
    
    # Distance between thumb tip (4) and index tip (8)
    distance = tracker.calculate_distance(hand.landmarks, 4, 8, w, h)
    
    if distance < 40:
        print("PINCH DETECTED!")
```

### Example 3: Track Hand Movement
```python
prev_position = None

if hand_results:
    hand = hand_results[0]
    wrist = hand.landmarks[0]  # Wrist landmark
    
    if prev_position:
        dx = wrist.x - prev_position.x
        dy = wrist.y - prev_position.y
        
        if abs(dx) > 0.1:
            print(f"Swipe {'Right' if dx > 0 else 'Left'}")
    
    prev_position = wrist
```

---

## 🏆 Project Quality Features

This project follows professional standards:

✅ **Type Hints** - Full type annotations for IDE support  
✅ **Docstrings** - Comprehensive documentation  
✅ **Error Handling** - Try-except blocks and validation  
✅ **Resource Management** - Context managers (`with` statements)  
✅ **Modular Design** - Separation of concerns  
✅ **Clean Code** - Following PEP 8 and best practices  
✅ **Beginner Friendly** - Extensive comments and examples  

---

## 📞 Need Help?

1. Check [README.md](README.md) for full documentation
2. Review code comments in each module
3. Check the troubleshooting section above
4. Verify all packages are installed: `pip list`

---

## 🎓 Learning Resources

- **MediaPipe Hands**: https://google.github.io/mediapipe/solutions/hands.html
- **OpenCV Tutorials**: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- **Python Type Hints**: https://docs.python.org/3/library/typing.html

---

**🎉 You're all set! Run `python -m src.main` to start building!**
