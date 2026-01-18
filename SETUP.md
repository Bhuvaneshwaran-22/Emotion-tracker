# Setup Instructions

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download MediaPipe Models (Automatic)
The system will automatically download required model files on first run:
- **face_landmarker.task** (10.6 MB) - Face detection model
- **hand_landmarker.task** (26.4 MB) - Hand tracking model

Models are downloaded from official Google MediaPipe CDN to `src/assets/` folder.

### 3. Run the Application
```bash
python -m src.main
```

**Controls:**
- `Q` or `ESC` - Quit
- `S` - Save screenshot
- `R` - Reset statistics

---

## Manual Model Download (Optional)

If you prefer to download models manually:

### Face Landmarker
```bash
curl -o src/assets/face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

### Hand Landmarker
```bash
curl -o src/assets/hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

---

## System Requirements

- **Python**: 3.10+
- **RAM**: 4GB minimum (8GB recommended)
- **Webcam**: Any USB or built-in camera
- **OS**: Windows 10/11 (Linux/Mac compatible)

---

## Troubleshooting

**Issue**: Models don't download automatically  
**Solution**: Check internet connection or use manual download commands above

**Issue**: Webcam not detected  
**Solution**: Ensure no other application is using the camera

**Issue**: Low FPS (<15)  
**Solution**: System automatically switches to light HUD mode for performance

---

For more details, see [README.md](README.md)
