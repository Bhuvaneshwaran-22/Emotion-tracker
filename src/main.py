"""
AIRCTRL - Emotion Intelligence System (CPU-only, webcam-first)

Architecture:
    Perception (FaceMesh) → Feature Extraction → Emotion Logic → Visualization
"""

import sys
import time
import argparse
from pathlib import Path
from collections import deque

import cv2
import numpy as np

from src.camera import Webcam
from src.emotion import Emotion, EmotionLogic, EmojiMapper, EmotionTracker
from src.vision import FaceTracker
from src.core.feature_logger import FeatureLogger
from src.core.config import load_config
from src.core.config import load_config


def draw_professional_hud(
    frame,
    fps: float,
    emotion: Emotion,
    confidence: float,
    features,
    stats: dict,
    fps_history: deque,
    show_history: bool = True,
    light_mode: bool = False,
) -> None:
    """Award-winning HUD with professional design and real-time analytics."""
    h, w, _ = frame.shape
    
    # Top panel - Main info with gradient
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 90), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
    
    # Title with glow effect
    cv2.putText(frame, "AIRCTRL", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 255), 3)
    cv2.putText(frame, "AIRCTRL", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
    subtitle = "Emotion Intelligence System" if not light_mode else "Light HUD (FPS protect)"
    cv2.putText(frame, subtitle, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    
    # Emotion display with color coding
    emotion_colors = {
        Emotion.HAPPY: (60, 220, 120),
        Emotion.SAD: (230, 180, 100),
        Emotion.ANGRY: (50, 50, 240),
        Emotion.SURPRISED: (100, 200, 255),
        Emotion.FEAR: (180, 160, 255),
        Emotion.DISGUST: (100, 200, 120),
        Emotion.EXCITED: (255, 170, 90),
        Emotion.NEUTRAL: (200, 200, 200),
    }
    emotion_color = emotion_colors.get(emotion, (200, 200, 200))
    
    cv2.putText(frame, f"Emotion: {emotion.value}", (w - 300, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, emotion_color, 2)
    
    # Confidence bar
    bar_width = 200
    bar_height = 15
    bar_x = w - 300
    bar_y = 50
    
    # Background bar
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (60, 60, 60), -1)
    # Confidence fill
    fill_width = int(bar_width * confidence)
    conf_color = (0, int(255 * confidence), int(255 * (1 - confidence)))
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), conf_color, -1)
    cv2.putText(frame, f"Confidence: {confidence*100:.0f}%", (bar_x, bar_y - 5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    # FPS with mini graph
    avg_fps = sum(fps_history) / len(fps_history) if fps_history else fps
    fps_color = (0, 255, 0) if fps > 25 else (0, 200, 255) if fps > 15 else (0, 100, 255)
    cv2.putText(frame, f"FPS: {fps:.1f}", (w - 100, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, fps_color, 1)
    
    # Bottom panel - Feature metrics
    panel_h = 120
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - panel_h), (450, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
    
    # Feature bars
    def draw_feature_bar(name, value, y_pos, max_val=0.1):
        bar_w = 350
        x = 15
        cv2.putText(frame, name, (x, y_pos - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        cv2.rectangle(frame, (x + 80, y_pos - 15), (x + 80 + bar_w, y_pos), (40, 40, 40), -1)
        fill = int(min(abs(value) / max_val, 1.0) * bar_w)
        color = (100, 200, 255) if value > 0 else (200, 100, 255)
        cv2.rectangle(frame, (x + 80, y_pos - 15), (x + 80 + fill, y_pos), color, -1)
        cv2.putText(frame, f"{value:.3f}", (x + 80 + bar_w + 5, y_pos - 3),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

    draw_feature_bar("Mouth:", features.mouth_openness, h - 90)
    draw_feature_bar("Eyes:", features.eye_openness, h - 60)
    draw_feature_bar("Brows:", features.eyebrow_raise, h - 30, max_val=0.05)

    # Right panel - Analytics (skip in light mode)
    if stats and show_history:
        panel_w = 250
        overlay = frame.copy()
        cv2.rectangle(overlay, (w - panel_w, 100), (w, 100 + 200), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        cv2.putText(frame, "Emotion History", (w - panel_w + 10, 125),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        y_offset = 150
        for emotion_name, data in sorted(stats.items(), key=lambda x: x[1]['percentage'], reverse=True):
            if data['percentage'] > 0:
                pct = data['percentage']
                cv2.putText(frame, f"{emotion_name[:3]}", (w - panel_w + 10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                bar_len = int((panel_w - 100) * pct / 100)
                cv2.rectangle(frame, (w - panel_w + 60, y_offset - 10),
                             (w - panel_w + 60 + bar_len, y_offset), emotion_colors.get(Emotion(emotion_name), (150, 150, 150)), -1)
                cv2.putText(frame, f"{pct:.0f}%", (w - panel_w + 60 + bar_len + 5, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)
                y_offset += 25
    
    # Controls hint
    cv2.putText(frame, "Controls: Q/ESC=Quit  S=Screenshot  R=Reset Stats", 
               (w // 2 - 200, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AIRCTRL - Emotion Intelligence System")
    parser.add_argument("--log", action="store_true", help="Enable benchmark logging to CSV")
    parser.add_argument("--log-path", type=str, default=None, help="Optional custom log file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    
    print("=" * 70)
    print("  🏆 AIRCTRL - Award-Winning Emotion Intelligence System 🏆")
    print("  Architecture: Perception → Features → Smoothing → Emotion → Visual")
    print("=" * 70)
    print("\n🎯 Professional Features:")
    print("   ✓ Temporal smoothing for jitter-free tracking")
    print("   ✓ Confidence scoring with stability analysis")
    print("   ✓ Real-time emotion analytics")
    print("   ✓ Professional UI with live metrics")
    print("   ✓ Externalized config (config.yaml)")
    print("\n⚠️  Security Notice:")
    print("   This system detects emotions from live video only.")
    print("   No liveness detection: photos/videos may be misclassified as live.")
    print("   For production, integrate face anti-spoofing (e.g., blink detection).")
    print("\n🎮 Controls:")
    print("   Q/ESC - Quit application")
    print("   S - Save screenshot")
    print("   R - Reset emotion statistics")
    print("\n🚀 Initializing...\n")

    webcam = Webcam(camera_index=config.camera.index, width=config.camera.width, height=config.camera.height, fps=config.camera.fps)
    face_tracker = FaceTracker(max_faces=config.face_detection.max_faces, min_detection_confidence=config.face_detection.min_detection_confidence, min_tracking_confidence=config.face_detection.min_tracking_confidence, draw_landmarks=config.face_detection.draw_landmarks)
    emotion_logic = EmotionLogic()
    emoji_mapper = EmojiMapper(Path(__file__).resolve().parent.parent / "assets" / "emojis")
    emotion_tracker = EmotionTracker(smoothing_factor=config.smoothing.smoothing_factor, history_size=config.smoothing.history_size, confidence_threshold=config.smoothing.confidence_threshold, min_dwell_frames=config.smoothing.min_dwell_frames, cooldown_frames=config.smoothing.cooldown_frames)

    feature_logger = FeatureLogger(Path(args.log_path)) if args.log else None
    if feature_logger:
        print(f"📝 Logging enabled → {feature_logger.path}")

    if not webcam.start():
        print("\n❌ Failed to start webcam. Close other apps or try another camera index.")
        sys.exit(1)

    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    screenshot_count = 0
    prev_time = time.time()
    fps_history = deque(maxlen=30)
    
    print("✓ All systems ready!\n")
    print("=" * 70)

    try:
        while True:
            ok, frame = webcam.read_frame()
            if not ok or frame is None:
                continue

            annotated_frame, faces = face_tracker.process_frame(frame)

            curr_time = time.time()
            fps = 1 / max(curr_time - prev_time, 1e-6)
            prev_time = curr_time
            fps_history.append(fps)
            avg_fps = sum(fps_history) / len(fps_history) if fps_history else fps
            light_mode = len(fps_history) == fps_history.maxlen and avg_fps < config.ui.fps_light_mode_threshold

            if faces:
                face = faces[0]
                raw_features = emotion_logic.compute_features(face.landmarks, face.bbox)
                raw_emotion = emotion_logic.infer_emotion(raw_features)
                
                # Apply temporal smoothing and get confidence
                emotion_state = emotion_tracker.update(raw_features, raw_emotion)
                stats = emotion_tracker.get_emotion_stats()

                # Optional benchmark logging
                if feature_logger:
                    feature_logger.log(
                        fps=fps,
                        features=emotion_state.smoothed_features,
                        emotion=emotion_state.emotion,
                        confidence=emotion_state.confidence,
                    )

                # Overlay emoji (skip in light mode to preserve FPS)
                if not light_mode:
                    emoji_img = emoji_mapper.get_emoji(emotion_state.emotion)
                    annotated_frame = emoji_mapper.overlay_emoji(annotated_frame, emoji_img, face.bbox, scale=config.ui.emoji_scale)

                # Draw bounding box with confidence
                h, w, _ = annotated_frame.shape
                x0, y0 = int(face.bbox.x_min * w), int(face.bbox.y_min * h)
                x1, y1 = int(face.bbox.x_max * w), int(face.bbox.y_max * h)
                
                conf_color = (
                    int(100 * (1 - emotion_state.confidence)),
                    int(255 * emotion_state.confidence),
                    int(100 * emotion_state.confidence)
                )
                cv2.rectangle(annotated_frame, (x0, y0), (x1, y1), conf_color, 3)
                cv2.putText(annotated_frame, f"{emotion_state.confidence*100:.0f}%", (x0, y0 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, conf_color, 2)

                draw_professional_hud(annotated_frame, fps, emotion_state.emotion, emotion_state.confidence,
                                    emotion_state.smoothed_features, stats, fps_history, show_history=not light_mode, light_mode=light_mode)

                print(f"\r🎭 {emotion_state.emotion.value:<10} | 📊 Conf: {emotion_state.confidence*100:5.1f}% | "
                      f"👄 {emotion_state.smoothed_features.mouth_openness:.3f} | "
                      f"👁 {emotion_state.smoothed_features.eye_openness:.3f} | 📈 FPS: {fps:.1f}  ", end="", flush=True)
            else:
                from src.vision.face_tracker import FaceBoundingBox
                dummy_features = emotion_logic.compute_features([(0,0,0)]*478, FaceBoundingBox(0,0,0,0))
                draw_professional_hud(annotated_frame, fps, Emotion.NEUTRAL, 0.0, dummy_features, {}, fps_history, show_history=not light_mode, light_mode=light_mode)
                cv2.putText(annotated_frame, "No face detected", (annotated_frame.shape[1]//2 - 150, annotated_frame.shape[0]//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 100, 255), 2)

            cv2.imshow("AIRCTRL - Emotion Intelligence System", annotated_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == 27:
                print("\n\n👋 Shutting down...")
                break
            elif key == ord("s"):
                screenshot_count += 1
                filename = screenshots_dir / f"airctrl_pro_{screenshot_count:03d}.png"
                cv2.imwrite(str(filename), annotated_frame)
                print(f"\n📸 Screenshot saved: {filename}")
            elif key == ord("r"):
                emotion_tracker.reset()
                print("\n🔄 Statistics reset")

    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C)")
    except Exception as exc:  # pragma: no cover - runtime guard
        print(f"\n❌ Error: {exc}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        if feature_logger:
            feature_logger.close()
        webcam.release()
        face_tracker.release()
        cv2.destroyAllWindows()
        print("✓ Shutdown complete")


if __name__ == "__main__":
    main()
