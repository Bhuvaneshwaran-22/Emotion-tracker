# AIRCTRL Production Deployment Guide

## Overview

This guide covers deploying AIRCTRL from hackathon demo to production-ready system.

---

## Quick Start (Docker)

```bash
# Build image
docker build -t airctrl:latest .

# Run container
docker run -it --rm \
  --device=/dev/video0:/dev/video0 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/logs:/app/logs \
  airctrl:latest
```

---

## System Requirements

### Minimum
- CPU: 4 cores @ 2.5 GHz
- RAM: 4 GB
- Webcam: 720p @ 30fps
- OS: Linux/macOS/Windows

### Recommended (Production)
- CPU: 8+ cores (for multi-face)
- RAM: 16 GB
- GPU: NVIDIA with CUDA (optional, for 60+ FPS)
- Network: 10 Gbps for video streaming

---

## Environment Setup

### 1. Install Dependencies

```bash
# System packages (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip libgl1-mesa-glx

# Python packages
pip install -r requirements.txt
pip install gunicorn prometheus-client  # For API deployment
```

### 2. Configure Settings

```bash
cp config.yaml config.prod.yaml
# Edit config.prod.yaml:
# - Set camera.index for prod webcam
# - Tune emotion_thresholds from calibration logs
# - Enable logging.enabled for monitoring
```

### 3. Security Hardening

- **Liveness Detection**: Integrate `face-anti-spoofing` library or blink counter.
- **Data Encryption**: TLS 1.3 for video streams, encrypt logs at rest.
- **Access Control**: API keys or OAuth2 for REST endpoints.

---

## Deployment Architectures

### Architecture 1: Single-Server (Demo/SMB)

```
[Webcam] → [AIRCTRL App] → [Local Display]
```

**Use case**: Kiosk, small office, classroom.  
**Capacity**: 1 face, 15-20 FPS.  
**Deploy**: Systemd service or Docker container.

### Architecture 2: REST API (Multi-Client)

```
[Clients] → [Load Balancer] → [FastAPI Server] → [AIRCTRL Worker Pool]
                                                    ↓
                                             [Redis Cache]
```

**Use case**: Web app, mobile app, multiple cameras.  
**Capacity**: 10+ concurrent streams.  
**Deploy**: K8s cluster with horizontal pod autoscaling.

**API Example**:
```python
# server.py
from fastapi import FastAPI, UploadFile
from src.emotion import EmotionLogic
from src.vision import FaceTracker

app = FastAPI()
tracker = FaceTracker()
logic = EmotionLogic()

@app.post("/detect")
async def detect_emotion(image: UploadFile):
    frame = await image.read()
    _, faces = tracker.process_frame(frame)
    if faces:
        features = logic.compute_features(faces[0].landmarks, faces[0].bbox)
        emotion = logic.infer_emotion(features)
        return {"emotion": emotion.value}
    return {"emotion": "NONE"}
```

### Architecture 3: Edge Deployment (IoT)

```
[Edge Device (Raspberry Pi)] → [AIRCTRL Lite] → [Cloud Analytics]
```

**Use case**: Smart mirrors, retail analytics, security.  
**Capacity**: 1 face, 10 FPS.  
**Deploy**: ONNX/TFLite on ARM64.

---

## Monitoring & Observability

### Prometheus Metrics

```python
# Add to main.py
from prometheus_client import Counter, Histogram, start_http_server

emotion_counter = Counter('emotions_detected', 'Total emotions detected', ['emotion'])
fps_histogram = Histogram('fps', 'Frames per second')

# In loop:
emotion_counter.labels(emotion=emotion_state.emotion.value).inc()
fps_histogram.observe(fps)

# Start metrics server
start_http_server(8000)
```

### Logging

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# In loop:
logger.info(f"Detected {emotion_state.emotion.value} with confidence {emotion_state.confidence:.2f}")
```

### Alerting

- **Low FPS**: Alert if avg FPS < 10 for > 5 minutes.
- **High Error Rate**: Alert if face detection fails > 50% over 10 minutes.
- **Confidence Drift**: Alert if avg confidence < 0.5 (model degradation).

---

## Performance Tuning

### Optimization 1: Lower Resolution

```yaml
# config.yaml
camera:
  width: 640
  height: 480  # Reduces compute by 4x
```

### Optimization 2: Skip Frames

```python
# Process every Nth frame
if frame_count % 3 == 0:
    annotated_frame, faces = face_tracker.process_frame(frame)
```

### Optimization 3: GPU Acceleration

```python
# MediaPipe with GPU
base_options = mp.tasks.BaseOptions(
    model_asset_path=str(model_path),
    delegate=mp.tasks.BaseOptions.Delegate.GPU  # Change from CPU
)
```

---

## Disaster Recovery

### Backup Strategy

- **Config**: Git-managed, versioned in repo.
- **Logs**: Daily rotation, compress and archive to S3/GCS.
- **Models**: Pin MediaPipe version, cache `.task` files.

### Failure Scenarios

| Scenario | Mitigation |
|----------|------------|
| Webcam disconnect | Auto-retry with exponential backoff |
| MediaPipe crash | Process restart via supervisor |
| High CPU spike | Enable light HUD mode automatically |
| Memory leak | Scheduled daily restart (cron) |

---

## Compliance & Ethics

### GDPR/CCPA

- **Consent**: Display banner before video capture.
- **Data Minimization**: Discard frames after processing, store only aggregated stats.
- **Right to Erasure**: API endpoint to delete user's emotion history.

### Bias Mitigation

- **Dataset Diversity**: Test on multiple ethnicities, ages, genders.
- **Fairness Metrics**: Report F1 scores per demographic group.
- **Human-in-the-Loop**: Flag low-confidence predictions for review.

---

## Support & Escalation

**Level 1 (Monitoring)**: Automated alerts via PagerDuty/Slack.  
**Level 2 (On-Call Engineer)**: Restart services, check logs, swap webcam.  
**Level 3 (ML Engineer)**: Retune thresholds, update MediaPipe model, debug false positives.

**Runbook**: See `docs/RUNBOOK.md` for step-by-step incident response.

---

## Cost Estimation

### AWS Deployment (t3.large, 8 hours/day)

- **Compute**: $0.0832/hour × 8 × 30 = ~$20/month
- **Storage**: Logs ~1 GB/day = ~$0.60/month
- **Bandwidth**: 100 GB egress = ~$9/month
- **Total**: ~$30/month for single-instance deployment

### Kubernetes (EKS, 3 replicas)

- **EKS Control Plane**: $72/month
- **Worker Nodes**: 3× t3.medium = ~$90/month
- **Load Balancer**: ~$20/month
- **Total**: ~$180/month for HA deployment

---

## Next Steps

1. **Pilot**: Deploy on 1-2 devices, collect 1 week of logs.
2. **Evaluate**: Run `scripts/evaluate.py` on real-world data.
3. **Tune**: Update `config.yaml` thresholds based on metrics.
4. **Scale**: Add replicas, enable GPU, integrate liveness detection.
5. **Monitor**: Set up Grafana dashboards for FPS, emotions, confidence.

---

**Questions?** Open an issue on GitHub or contact the maintainers.
