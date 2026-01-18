"""
Evaluation script for AIRCTRL emotion detection.

Computes precision, recall, F1 per emotion on manually annotated frames.
Requires annotations CSV: frame_id,ground_truth_emotion
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import cv2

from src.emotion import Emotion, EmotionLogic
from src.vision import FaceTracker


@dataclass
class EvalMetrics:
    precision: float
    recall: float
    f1: float
    support: int


def compute_metrics(y_true: List[Emotion], y_pred: List[Emotion]) -> Dict[Emotion, EvalMetrics]:
    """Compute per-class precision, recall, F1."""
    emotions = set(y_true) | set(y_pred)
    results = {}
    
    for emotion in emotions:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == emotion and p == emotion)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != emotion and p == emotion)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == emotion and p != emotion)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        support = sum(1 for t in y_true if t == emotion)
        
        results[emotion] = EvalMetrics(precision, recall, f1, support)
    
    return results


def evaluate(annotations_csv: Path, frames_dir: Path) -> None:
    """Run evaluation on annotated frames."""
    print("=" * 70)
    print("  AIRCTRL Evaluation")
    print("=" * 70)
    
    # Load annotations
    annotations = {}
    with annotations_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            annotations[row["frame_id"]] = Emotion(row["ground_truth"])
    
    print(f"\n✓ Loaded {len(annotations)} annotations")
    
    # Initialize system
    face_tracker = FaceTracker(max_faces=1, min_detection_confidence=0.7)
    emotion_logic = EmotionLogic()
    
    # Predict
    y_true = []
    y_pred = []
    skipped = 0
    
    for frame_id, ground_truth in annotations.items():
        frame_path = frames_dir / f"{frame_id}.png"
        if not frame_path.exists():
            skipped += 1
            continue
        
        frame = cv2.imread(str(frame_path))
        _, faces = face_tracker.process_frame(frame)
        
        if not faces:
            skipped += 1
            continue
        
        features = emotion_logic.compute_features(faces[0].landmarks, faces[0].bbox)
        predicted = emotion_logic.infer_emotion(features)
        
        y_true.append(ground_truth)
        y_pred.append(predicted)
    
    print(f"✓ Evaluated {len(y_true)} frames (skipped {skipped})")
    
    # Compute metrics
    metrics = compute_metrics(y_true, y_pred)
    
    print("\n" + "=" * 70)
    print("Per-Emotion Metrics")
    print("=" * 70)
    print(f"{'Emotion':<12} {'Precision':<12} {'Recall':<12} {'F1':<12} {'Support':<8}")
    print("-" * 70)
    
    for emotion, metric in sorted(metrics.items(), key=lambda x: x[1].support, reverse=True):
        print(f"{emotion.value:<12} {metric.precision:<12.3f} {metric.recall:<12.3f} {metric.f1:<12.3f} {metric.support:<8}")
    
    # Overall accuracy
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)
    macro_f1 = sum(m.f1 for m in metrics.values()) / len(metrics)
    
    print("-" * 70)
    print(f"{'Overall':<12} {'Accuracy':<12} {'Macro F1':<12}")
    print(f"{'':12} {accuracy:<12.3f} {macro_f1:<12.3f}")
    print("=" * 70)
    
    face_tracker.release()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate AIRCTRL on annotated frames")
    parser.add_argument("--annotations", type=str, required=True, help="Path to annotations CSV")
    parser.add_argument("--frames", type=str, required=True, help="Directory containing frame images")
    args = parser.parse_args()
    
    evaluate(Path(args.annotations), Path(args.frames))
