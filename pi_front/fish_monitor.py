#!/usr/bin/env python3
"""
Front-camera fish behavior demo for Raspberry Pi 4 + Google Coral USB Edge TPU.

Pipeline:
    frame -> YOLO EdgeTPU detection -> ByteTrack -> short-gap interpolation
    -> 5-frame centered median cleaning -> 5 s behavior features
    -> RandomForest behavior classifier -> 65/35 demo UI

Scientific constraints preserved from Notebooks 10-13:
- Track ID is tracker identity, NOT guaranteed biological identity.
- Short gaps: interpolate at most 3 missing source frames.
- Long gaps: reset trajectory segment.
- Smoothing: centered rolling median, window 5.
- Behavior window: 5 s.
- Behavior update: every 1 s.
- Four model classes:
    NORMAL_SWIM, PAIR_INTERACTION, SHELTER_TRANSITION, FEEDING
- Distance/speed remain px and px/s until geometric calibration is available.

This script is intentionally self-contained and does not modify research results.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import cv2
import joblib
import numpy as np


MODEL_FEATURE_COLUMNS = [
    "coverage_ratio",
    "observed_ratio",
    "interpolated_ratio",
    "distance_5s_px",
    "distance_last_1s_px",
    "net_displacement_px",
    "path_efficiency",
    "mean_speed_px_s",
    "median_speed_px_s",
    "max_speed_px_s",
    "speed_std_px_s",
    "mean_speed_norm_s",
    "max_speed_norm_s",
    "mean_abs_accel_px_s2",
    "mean_abs_turn_rad",
    "immobile_ratio",
    "x_mean_norm",
    "x_std_norm",
    "x_range_norm",
    "y_mean_norm",
    "y_std_norm",
    "y_range_norm",
    "bbox_area_mean_norm",
]

MODEL_BEHAVIOR_CLASSES = [
    "NORMAL_SWIM",
    "PAIR_INTERACTION",
    "SHELTER_TRANSITION",
    "FEEDING",
]

WINDOW_SEC = 5.0
STEP_SEC = 1.0
TRAILING_DISTANCE_SEC = 1.0
MIN_WINDOW_COVERAGE = 0.60
IMMOBILE_SPEED_NORM_S = 0.01

MAX_INTERP_GAP_FRAMES = 3
SMOOTH_WINDOW_FRAMES = 5
# Two source frames of feature latency make centered smoothing closer to N10 offline behavior.
FEATURE_LATENCY_FRAMES = 2

TAIL_SEC = 1.0
TRACK_STALE_SEC = 2.0
HISTORY_KEEP_SEC = 8.0


def safe_mean(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return float(np.mean(x)) if len(x) else float("nan")


def safe_median(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return float(np.median(x)) if len(x) else float("nan")


def safe_std(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return float(np.std(x)) if len(x) else float("nan")


def centered_rolling_median(values: np.ndarray, window: int = 5) -> np.ndarray:
    """Match pandas rolling(window, center=True, min_periods=1).median() used in N10."""
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n == 0:
        return values.copy()

    w = min(int(window), n)
    if w % 2 == 0:
        w = max(1, w - 1)
    half = w // 2

    out = np.empty(n, dtype=float)
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        out[i] = float(np.nanmedian(values[lo:hi]))
    return out


@dataclass
class TrackSample:
    frame_index: int
    time_sec: float
    cx_raw: float
    cy_raw: float
    bbox_area: float
    confidence: float
    observed: bool
    interpolated: bool


@dataclass
class TrackState:
    track_id: int
    frame_width: int
    frame_height: int
    fps_source: float

    samples: List[TrackSample] = field(default_factory=list)
    last_frame_index: Optional[int] = None
    last_seen_time_sec: Optional[float] = None

    behavior: str = "WARMUP"
    behavior_conf: float = float("nan")
    last_feature_end_sec: float = -1e9

    distance_last_1s_px: float = float("nan")
    mean_speed_px_s: float = float("nan")
    coverage_ratio: float = float("nan")

    def reset_segment(self) -> None:
        self.samples.clear()
        self.last_frame_index = None
        self.behavior = "WARMUP"
        self.behavior_conf = float("nan")
        self.last_feature_end_sec = -1e9
        self.distance_last_1s_px = float("nan")
        self.mean_speed_px_s = float("nan")
        self.coverage_ratio = float("nan")

    def add_observation(
        self,
        frame_index: int,
        time_sec: float,
        xyxy: Tuple[float, float, float, float],
        confidence: float,
    ) -> None:
        x1, y1, x2, y2 = map(float, xyxy)
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        area = max(0.0, x2 - x1) * max(0.0, y2 - y1)

        if self.last_frame_index is not None and self.samples:
            frame_diff = int(frame_index - self.last_frame_index)

            # N10: new segment if frame_diff > MAX_INTERP_GAP_FRAMES + 1.
            if frame_diff > (MAX_INTERP_GAP_FRAMES + 1) or frame_diff <= 0:
                self.reset_segment()

            elif frame_diff > 1:
                prev = self.samples[-1]
                missing = frame_diff - 1

                # Missing <= 3 here because a larger gap was reset above.
                for j in range(1, missing + 1):
                    alpha = j / float(frame_diff)
                    self.samples.append(
                        TrackSample(
                            frame_index=prev.frame_index + j,
                            time_sec=prev.time_sec + alpha * (time_sec - prev.time_sec),
                            cx_raw=prev.cx_raw + alpha * (cx - prev.cx_raw),
                            cy_raw=prev.cy_raw + alpha * (cy - prev.cy_raw),
                            bbox_area=prev.bbox_area + alpha * (area - prev.bbox_area),
                            confidence=prev.confidence + alpha * (confidence - prev.confidence),
                            observed=False,
                            interpolated=True,
                        )
                    )

        self.samples.append(
            TrackSample(
                frame_index=int(frame_index),
                time_sec=float(time_sec),
                cx_raw=float(cx),
                cy_raw=float(cy),
                bbox_area=float(area),
                confidence=float(confidence),
                observed=True,
                interpolated=False,
            )
        )

        self.last_frame_index = int(frame_index)
        self.last_seen_time_sec = float(time_sec)

        cutoff = float(time_sec) - HISTORY_KEEP_SEC
        if len(self.samples) > 10:
            self.samples = [s for s in self.samples if s.time_sec >= cutoff]

    def _clean_arrays(self) -> Optional[Dict[str, np.ndarray]]:
        if len(self.samples) < 2:
            return None

        s = sorted(self.samples, key=lambda x: x.frame_index)

        frame_index = np.asarray([v.frame_index for v in s], dtype=int)
        time_sec = np.asarray([v.time_sec for v in s], dtype=float)
        cx_raw = np.asarray([v.cx_raw for v in s], dtype=float)
        cy_raw = np.asarray([v.cy_raw for v in s], dtype=float)
        bbox_area = np.asarray([v.bbox_area for v in s], dtype=float)
        observed = np.asarray([v.observed for v in s], dtype=bool)
        interpolated = np.asarray([v.interpolated for v in s], dtype=bool)

        cx_clean = centered_rolling_median(cx_raw, SMOOTH_WINDOW_FRAMES)
        cy_clean = centered_rolling_median(cy_raw, SMOOTH_WINDOW_FRAMES)

        return {
            "frame_index": frame_index,
            "time_sec": time_sec,
            "cx_clean": cx_clean,
            "cy_clean": cy_clean,
            "bbox_area": bbox_area,
            "observed": observed,
            "interpolated": interpolated,
            "x_norm": cx_clean / float(self.frame_width),
            "y_norm": cy_clean / float(self.frame_height),
        }

    def tail_points(self, now_sec: float, tail_sec: float = TAIL_SEC) -> List[Tuple[int, int]]:
        arr = self._clean_arrays()
        if arr is None:
            return []

        mask = arr["time_sec"] >= (float(now_sec) - float(tail_sec))
        xs = arr["cx_clean"][mask]
        ys = arr["cy_clean"][mask]
        return [(int(round(x)), int(round(y))) for x, y in zip(xs, ys)]

    def behavior_features(self) -> Optional[Tuple[float, Dict[str, float]]]:
        arr = self._clean_arrays()
        if arr is None:
            return None

        n = len(arr["time_sec"])
        if n < 3:
            return None

        latency = min(FEATURE_LATENCY_FRAMES, n - 1)
        eligible_idx = n - 1 - latency

        # N11 windows are [start, end). Add one frame period so eligible sample is included.
        end = float(arr["time_sec"][eligible_idx]) + (1.0 / float(self.fps_source))
        start = end - WINDOW_SEC

        if float(arr["time_sec"][0]) > start + (1.0 / float(self.fps_source)):
            return None

        mask = (arr["time_sec"] >= start) & (arr["time_sec"] < end)
        idx = np.flatnonzero(mask)
        if len(idx) < 2:
            return None

        t = arr["time_sec"][idx]
        cx = arr["cx_clean"][idx]
        cy = arr["cy_clean"][idx]
        x_norm = arr["x_norm"][idx]
        y_norm = arr["y_norm"][idx]
        bbox_area = arr["bbox_area"][idx]
        observed = arr["observed"][idx]
        interpolated = arr["interpolated"][idx]

        fps = float(self.fps_source)
        expected = max(1, int(round((end - start) * fps)))
        coverage = min(1.0, len(idx) / float(expected))
        if coverage < MIN_WINDOW_COVERAGE:
            return None

        dt = np.diff(t, prepend=np.nan)
        dx = np.diff(cx, prepend=np.nan)
        dy = np.diff(cy, prepend=np.nan)

        step = np.hypot(dx, dy)
        speed = np.divide(
            step,
            dt,
            out=np.full_like(step, np.nan, dtype=float),
            where=dt > 0,
        )

        diag = math.hypot(float(self.frame_width), float(self.frame_height))
        speed_norm = speed / diag if diag > 0 else np.full_like(speed, np.nan)

        angle = np.arctan2(dy, dx)
        dangle = np.diff(angle)
        dangle = (dangle + np.pi) % (2 * np.pi) - np.pi

        distance = float(np.nansum(step[np.isfinite(step)]))

        net = float(math.hypot(cx[-1] - cx[0], cy[-1] - cy[0]))
        efficiency = net / distance if distance > 1e-9 else 0.0

        accel = np.diff(speed)
        dt2 = dt[2:] if len(dt) >= 3 else np.asarray([], dtype=float)
        if len(dt2):
            accel_rate = np.divide(
                accel[1:] if len(accel) >= 2 else np.asarray([], dtype=float),
                dt2,
                out=np.full_like(dt2, np.nan, dtype=float),
                where=dt2 > 0,
            )
        else:
            accel_rate = np.asarray([], dtype=float)

        tail_start = max(start, end - TRAILING_DISTANCE_SEC)
        tail_mask = t >= tail_start
        tail_cx = cx[tail_mask]
        tail_cy = cy[tail_mask]
        if len(tail_cx) >= 2:
            tail_distance = float(
                np.nansum(
                    np.hypot(
                        np.diff(tail_cx),
                        np.diff(tail_cy),
                    )
                )
            )
        else:
            tail_distance = 0.0

        speed_norm_valid = speed_norm[np.isfinite(speed_norm)]
        immobile_ratio = (
            float(np.mean(speed_norm_valid < IMMOBILE_SPEED_NORM_S))
            if len(speed_norm_valid)
            else float("nan")
        )

        features = {
            "coverage_ratio": float(coverage),
            "observed_ratio": float(np.mean(observed.astype(float))),
            "interpolated_ratio": float(np.mean(interpolated.astype(float))),
            "distance_5s_px": distance,
            "distance_last_1s_px": tail_distance,
            "net_displacement_px": net,
            "path_efficiency": float(efficiency),
            "mean_speed_px_s": safe_mean(speed),
            "median_speed_px_s": safe_median(speed),
            "max_speed_px_s": float(np.nanmax(speed)) if np.isfinite(speed).any() else float("nan"),
            "speed_std_px_s": safe_std(speed),
            "mean_speed_norm_s": safe_mean(speed_norm),
            "max_speed_norm_s": float(np.nanmax(speed_norm)) if np.isfinite(speed_norm).any() else float("nan"),
            "mean_abs_accel_px_s2": safe_mean(np.abs(accel_rate)),
            "mean_abs_turn_rad": safe_mean(np.abs(dangle)),
            "immobile_ratio": immobile_ratio,
            "x_mean_norm": float(np.mean(x_norm)),
            "x_std_norm": float(np.std(x_norm)),
            "x_range_norm": float(np.max(x_norm) - np.min(x_norm)),
            "y_mean_norm": float(np.mean(y_norm)),
            "y_std_norm": float(np.std(y_norm)),
            "y_range_norm": float(np.max(y_norm) - np.min(y_norm)),
            "bbox_area_mean_norm": float(
                np.mean(bbox_area / float(self.frame_width * self.frame_height))
            ),
        }

        return end, features


class BehaviorModel:
    def __init__(
        self,
        model_path: Optional[Path],
        schema_path: Optional[Path],
        metadata_path: Optional[Path],
    ) -> None:
        self.model = None
        self.feature_columns = list(MODEL_FEATURE_COLUMNS)
        self.classes = list(MODEL_BEHAVIOR_CLASSES)
        self.metadata: Dict[str, Any] = {}

        if schema_path and schema_path.exists():
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            cols = schema.get("feature_columns")
            if cols:
                self.feature_columns = list(cols)

        if metadata_path and metadata_path.exists():
            self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            classes = self.metadata.get("classes")
            if classes:
                self.classes = list(classes)

        if model_path:
            if not model_path.exists():
                raise FileNotFoundError(f"Behavior model not found: {model_path}")
            self.model = joblib.load(model_path)

        if self.feature_columns != MODEL_FEATURE_COLUMNS:
            missing = [c for c in self.feature_columns if c not in MODEL_FEATURE_COLUMNS]
            if missing:
                raise RuntimeError(
                    "Deployment feature schema contains unsupported columns: "
                    + ", ".join(missing)
                )

    def predict(self, features: Dict[str, float]) -> Tuple[str, float]:
        if self.model is None:
            return "N/A", float("nan")

        x = np.asarray(
            [[features[c] for c in self.feature_columns]],
            dtype=float,
        )

        if not np.isfinite(x).all():
            return "WARMUP", float("nan")

        label = str(self.model.predict(x)[0])
        confidence = float("nan")

        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(x)[0]
            classes = [str(c) for c in self.model.classes_]
            if label in classes:
                confidence = float(proba[classes.index(label)])
            elif len(proba):
                confidence = float(np.max(proba))

        return label, confidence


class TelemetryRecorder:
    def __init__(
        self,
        out_root: Path,
        display_size: Tuple[int, int],
        record_fps: float,
    ) -> None:
        self.out_root = out_root
        self.display_size = display_size
        self.record_fps = max(1.0, float(record_fps))

        self.session_dir: Optional[Path] = None
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.csv_file = None
        self.csv_writer = None
        self.active = False

    def start(self) -> None:
        if self.active:
            return

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.out_root / stamp
        self.session_dir.mkdir(parents=True, exist_ok=True)

        video_path = self.session_dir / "front_demo_overlay.mp4"
        telemetry_path = self.session_dir / "front_demo_telemetry.csv"

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter(
            str(video_path),
            fourcc,
            self.record_fps,
            self.display_size,
        )

        if not self.video_writer.isOpened():
            self.video_writer.release()
            self.video_writer = None
            raise RuntimeError(f"Cannot open video writer: {video_path}")

        self.csv_file = telemetry_path.open("w", newline="", encoding="utf-8")
        self.csv_writer = csv.DictWriter(
            self.csv_file,
            fieldnames=[
                "wall_time_iso",
                "frame_index",
                "source_time_sec",
                "track_id",
                "behavior",
                "behavior_confidence",
                "distance_last_1s_px",
                "mean_speed_px_s",
                "coverage_ratio",
                "nn_inference_ms",
                "pipeline_fps",
            ],
        )
        self.csv_writer.writeheader()
        self.active = True

        print(f"[REC] session: {self.session_dir}")

    def stop(self) -> None:
        if self.video_writer is not None:
            self.video_writer.release()
        if self.csv_file is not None:
            self.csv_file.flush()
            self.csv_file.close()

        self.video_writer = None
        self.csv_file = None
        self.csv_writer = None
        self.active = False

    def toggle(self) -> None:
        if self.active:
            self.stop()
            print("[REC] stopped")
        else:
            self.start()

    def write_frame(self, frame: np.ndarray) -> None:
        if self.active and self.video_writer is not None:
            self.video_writer.write(frame)

    def log_behavior(
        self,
        frame_index: int,
        source_time_sec: float,
        track: TrackState,
        nn_inference_ms: float,
        pipeline_fps: float,
    ) -> None:
        if not self.active or self.csv_writer is None:
            return

        self.csv_writer.writerow(
            {
                "wall_time_iso": datetime.now().isoformat(timespec="milliseconds"),
                "frame_index": int(frame_index),
                "source_time_sec": f"{source_time_sec:.6f}",
                "track_id": int(track.track_id),
                "behavior": track.behavior,
                "behavior_confidence": (
                    f"{track.behavior_conf:.6f}"
                    if np.isfinite(track.behavior_conf)
                    else ""
                ),
                "distance_last_1s_px": (
                    f"{track.distance_last_1s_px:.6f}"
                    if np.isfinite(track.distance_last_1s_px)
                    else ""
                ),
                "mean_speed_px_s": (
                    f"{track.mean_speed_px_s:.6f}"
                    if np.isfinite(track.mean_speed_px_s)
                    else ""
                ),
                "coverage_ratio": (
                    f"{track.coverage_ratio:.6f}"
                    if np.isfinite(track.coverage_ratio)
                    else ""
                ),
                "nn_inference_ms": (
                    f"{nn_inference_ms:.3f}"
                    if np.isfinite(nn_inference_ms)
                    else ""
                ),
                "pipeline_fps": (
                    f"{pipeline_fps:.3f}"
                    if np.isfinite(pipeline_fps)
                    else ""
                ),
            }
        )
        self.csv_file.flush()


def parse_source(value: str):
    return int(value) if value.isdigit() else value


def fit_into(
    image: np.ndarray,
    width: int,
    height: int,
) -> np.ndarray:
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    h, w = image.shape[:2]
    if h <= 0 or w <= 0:
        return canvas

    scale = min(width / float(w), height / float(h))
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    resized = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_AREA)

    x = (width - nw) // 2
    y = (height - nh) // 2
    canvas[y : y + nh, x : x + nw] = resized
    return canvas


def put_text(
    image: np.ndarray,
    text: str,
    xy: Tuple[int, int],
    scale: float = 0.55,
    thickness: int = 1,
    color: Tuple[int, int, int] = (235, 235, 235),
) -> None:
    cv2.putText(
        image,
        text,
        xy,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def compact_behavior(label: str) -> str:
    mapping = {
        "NORMAL_SWIM": "NORMAL",
        "PAIR_INTERACTION": "PAIR",
        "SHELTER_TRANSITION": "SHELTER",
        "FEEDING": "FEEDING",
        "WARMUP": "WARMUP",
        "N/A": "N/A",
    }
    return mapping.get(label, label[:10])


class FishMonitor:
    def __init__(self, args: argparse.Namespace) -> None:
        from ultralytics import YOLO

        self.args = args
        self.det_model_path = Path(args.det_model).expanduser().resolve()
        if not self.det_model_path.exists():
            raise FileNotFoundError(f"Detection model not found: {self.det_model_path}")

        self.edge_tpu_requested = self.det_model_path.name.endswith("_edgetpu.tflite")
        if not self.edge_tpu_requested:
            print(
                "[WARN] Detection model does not end with '_edgetpu.tflite'. "
                "Coral acceleration will not be claimed."
            )

        self.detector = YOLO(str(self.det_model_path))
        self.coral_status = "WAIT" if self.edge_tpu_requested else "NON-TPU"

        behavior_model_path = Path(args.behavior_model).expanduser().resolve() if args.behavior_model else None
        schema_path = Path(args.schema).expanduser().resolve() if args.schema else None
        metadata_path = Path(args.metadata).expanduser().resolve() if args.metadata else None

        self.behavior_model = BehaviorModel(
            behavior_model_path,
            schema_path,
            metadata_path,
        )

        self.source = parse_source(args.source)
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open source: {args.source}")

        if isinstance(self.source, int):
            if args.camera_width:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(args.camera_width))
            if args.camera_height:
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(args.camera_height))
            if args.camera_fps:
                self.cap.set(cv2.CAP_PROP_FPS, float(args.camera_fps))

        fps = float(self.cap.get(cv2.CAP_PROP_FPS))
        if not np.isfinite(fps) or fps <= 1e-3:
            fps = float(args.camera_fps or 30.0)
        self.fps_source = fps

        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or int(args.camera_width or 1280)
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or int(args.camera_height or 720)

        self.frame_index = 0
        self.tracks: Dict[int, TrackState] = {}

        self.nn_inference_ms = float("nan")
        self.pipeline_fps = float("nan")
        self._fps_ema = None

        self.display_w = int(args.display_width)
        self.display_h = int(args.display_height)
        self.left_w = int(round(self.display_w * float(args.video_fraction)))
        self.left_w = min(max(100, self.left_w), self.display_w - 180)
        self.panel_w = self.display_w - self.left_w

        record_fps = min(float(self.fps_source), float(args.record_fps))
        self.recorder = TelemetryRecorder(
            out_root=Path(args.output_dir).expanduser().resolve(),
            display_size=(self.display_w, self.display_h),
            record_fps=record_fps,
        )

        if args.record:
            self.recorder.start()

        self.window_name = "Fish AI Front Demo"

    def source_time_sec(self) -> float:
        if isinstance(self.source, int):
            # For a live camera, use nominal source-frame time. This preserves px/s
            # interpretation used in the training videos, assuming sequential capture.
            return self.frame_index / float(self.fps_source)
        pos_ms = float(self.cap.get(cv2.CAP_PROP_POS_MSEC))
        if np.isfinite(pos_ms) and pos_ms > 0:
            return pos_ms / 1000.0
        return self.frame_index / float(self.fps_source)

    def run_detector(self, frame: np.ndarray):
        kwargs = {
            "source": frame,
            "persist": True,
            "tracker": self.args.tracker,
            "conf": float(self.args.conf),
            "iou": float(self.args.iou),
            "verbose": False,
        }

        if self.args.imgsz:
            kwargs["imgsz"] = int(self.args.imgsz)

        if self.args.tpu_device:
            kwargs["device"] = self.args.tpu_device

        t0 = time.perf_counter()
        results = self.detector.track(**kwargs)
        total_ms = (time.perf_counter() - t0) * 1000.0

        result = results[0]
        speed = getattr(result, "speed", None) or {}
        inference_ms = speed.get("inference", None)
        self.nn_inference_ms = (
            float(inference_ms)
            if inference_ms is not None
            else float(total_ms)
        )

        if self.edge_tpu_requested:
            self.coral_status = "ACTIVE"

        return result

    def update_fps(self, elapsed_sec: float) -> None:
        instant = 1.0 / max(elapsed_sec, 1e-9)
        alpha = 0.12
        self._fps_ema = instant if self._fps_ema is None else (
            alpha * instant + (1.0 - alpha) * self._fps_ema
        )
        self.pipeline_fps = float(self._fps_ema)

    def update_tracks(
        self,
        result,
        source_time_sec: float,
    ) -> List[Tuple[int, Tuple[int, int, int, int], float]]:
        current: List[Tuple[int, Tuple[int, int, int, int], float]] = []

        boxes = result.boxes
        if boxes is None or boxes.id is None or len(boxes) == 0:
            return current

        xyxy = boxes.xyxy.cpu().numpy()
        ids = boxes.id.int().cpu().tolist()
        confs = boxes.conf.cpu().numpy().tolist()

        for box, tid, conf in zip(xyxy, ids, confs):
            tid = int(tid)

            if tid not in self.tracks:
                self.tracks[tid] = TrackState(
                    track_id=tid,
                    frame_width=self.frame_width,
                    frame_height=self.frame_height,
                    fps_source=self.fps_source,
                )

            state = self.tracks[tid]
            state.add_observation(
                frame_index=self.frame_index,
                time_sec=source_time_sec,
                xyxy=tuple(map(float, box)),
                confidence=float(conf),
            )

            x1, y1, x2, y2 = map(lambda v: int(round(float(v))), box)
            current.append((tid, (x1, y1, x2, y2), float(conf)))

        return current

    def update_behavior(
        self,
        current_ids: List[int],
    ) -> None:
        for tid in current_ids:
            state = self.tracks[tid]
            payload = state.behavior_features()
            if payload is None:
                continue

            feature_end, features = payload
            if feature_end - state.last_feature_end_sec < STEP_SEC - 1e-6:
                continue

            state.last_feature_end_sec = float(feature_end)
            state.distance_last_1s_px = float(features["distance_last_1s_px"])
            state.mean_speed_px_s = float(features["mean_speed_px_s"])
            state.coverage_ratio = float(features["coverage_ratio"])

            label, confidence = self.behavior_model.predict(features)
            state.behavior = label
            state.behavior_conf = confidence

            self.recorder.log_behavior(
                frame_index=self.frame_index,
                source_time_sec=feature_end,
                track=state,
                nn_inference_ms=self.nn_inference_ms,
                pipeline_fps=self.pipeline_fps,
            )

    def draw_video(
        self,
        frame: np.ndarray,
        current: List[Tuple[int, Tuple[int, int, int, int], float]],
        source_time_sec: float,
    ) -> np.ndarray:
        out = frame.copy()

        for tid, (x1, y1, x2, y2), det_conf in current:
            state = self.tracks[tid]

            cv2.rectangle(
                out,
                (x1, y1),
                (x2, y2),
                (60, 220, 60),
                2,
            )

            label = f"ID {tid}  {det_conf:.2f}"
            put_text(
                out,
                label,
                (max(0, x1), max(22, y1 - 7)),
                scale=0.60,
                thickness=2,
                color=(255, 255, 255),
            )

            pts = state.tail_points(source_time_sec, TAIL_SEC)
            for a, b in zip(pts[:-1], pts[1:]):
                cv2.line(
                    out,
                    a,
                    b,
                    (255, 220, 40),
                    2,
                    cv2.LINE_AA,
                )

        put_text(
            out,
            "FRONT CAMERA",
            (14, 28),
            scale=0.72,
            thickness=2,
        )

        return out

    def draw_panel(
        self,
        current_ids: List[int],
    ) -> np.ndarray:
        panel = np.zeros((self.display_h, self.panel_w, 3), dtype=np.uint8)

        x = 12
        y = 28

        put_text(panel, "FISH AI MONITOR", (x, y), 0.62, 2)
        y += 27

        coral_color = (60, 220, 60) if self.coral_status == "ACTIVE" else (80, 190, 255)
        put_text(
            panel,
            f"Coral: {self.coral_status}",
            (x, y),
            0.52,
            1,
            coral_color,
        )
        y += 22

        nn_text = (
            f"NN: {self.nn_inference_ms:.1f} ms"
            if np.isfinite(self.nn_inference_ms)
            else "NN: --"
        )
        put_text(panel, nn_text, (x, y), 0.50, 1)
        y += 21

        fps_text = (
            f"Pipeline: {self.pipeline_fps:.1f} FPS"
            if np.isfinite(self.pipeline_fps)
            else "Pipeline: --"
        )
        put_text(panel, fps_text, (x, y), 0.50, 1)
        y += 21

        rec_text = "REC: ON" if self.recorder.active else "REC: OFF"
        rec_color = (70, 70, 255) if self.recorder.active else (170, 170, 170)
        put_text(panel, rec_text, (x, y), 0.50, 1, rec_color)

        y += 28
        cv2.line(panel, (8, y), (self.panel_w - 8, y), (80, 80, 80), 1)
        y += 24

        put_text(panel, f"Active tracks: {len(current_ids)}", (x, y), 0.52, 1)
        y += 25

        max_rows = max(1, (self.display_h - y - 54) // 47)

        for tid in sorted(current_ids)[:max_rows]:
            state = self.tracks[tid]

            behavior = compact_behavior(state.behavior)
            conf = (
                f"{state.behavior_conf * 100:.0f}%"
                if np.isfinite(state.behavior_conf)
                else "--"
            )

            put_text(
                panel,
                f"ID {tid:>3}  {behavior:<8} {conf:>4}",
                (x, y),
                0.49,
                1,
            )
            y += 20

            d = (
                f"{state.distance_last_1s_px:.0f}"
                if np.isfinite(state.distance_last_1s_px)
                else "--"
            )
            v = (
                f"{state.mean_speed_px_s:.0f}"
                if np.isfinite(state.mean_speed_px_s)
                else "--"
            )

            put_text(
                panel,
                f"d1s={d} px   v={v} px/s",
                (x + 6, y),
                0.43,
                1,
                (190, 190, 190),
            )
            y += 27

        footer_y = self.display_h - 35
        cv2.line(
            panel,
            (8, footer_y - 15),
            (self.panel_w - 8, footer_y - 15),
            (70, 70, 70),
            1,
        )
        put_text(
            panel,
            "ID = tracker identity",
            (x, footer_y),
            0.40,
            1,
            (160, 160, 160),
        )
        put_text(
            panel,
            "Behavior = experimental 4-class",
            (x, footer_y + 17),
            0.36,
            1,
            (145, 145, 145),
        )

        return panel

    def compose(
        self,
        video_frame: np.ndarray,
        panel: np.ndarray,
    ) -> np.ndarray:
        left = fit_into(video_frame, self.left_w, self.display_h)
        return np.hstack([left, panel])

    def cleanup_stale(self, now_sec: float) -> None:
        stale = []
        for tid, state in self.tracks.items():
            if state.last_seen_time_sec is None:
                continue
            if float(now_sec) - float(state.last_seen_time_sec) > TRACK_STALE_SEC:
                stale.append(tid)

        for tid in stale:
            del self.tracks[tid]

    def run(self) -> None:
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.display_w, self.display_h)

        if self.args.fullscreen:
            cv2.setWindowProperty(
                self.window_name,
                cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN,
            )

        print("")
        print("Controls:")
        print("  q / ESC : quit")
        print("  r       : toggle recording")
        print("")
        print(f"Source FPS: {self.fps_source:.3f}")
        print(f"Display: {self.display_w}x{self.display_h}")
        print(f"Detector: {self.det_model_path}")
        print(f"Tracker: {self.args.tracker}")
        print("")

        try:
            while True:
                loop_t0 = time.perf_counter()

                ok, frame = self.cap.read()
                if not ok:
                    print("[INFO] source ended or camera read failed.")
                    break

                # Update geometry if camera negotiated a different size.
                h, w = frame.shape[:2]
                if (w, h) != (self.frame_width, self.frame_height):
                    self.frame_width = int(w)
                    self.frame_height = int(h)
                    for state in self.tracks.values():
                        state.frame_width = int(w)
                        state.frame_height = int(h)

                source_time_sec = self.source_time_sec()

                try:
                    result = self.run_detector(frame)
                except Exception as exc:
                    self.coral_status = "ERROR"
                    raise RuntimeError(
                        "Detection/tracking failed. If using Coral, verify the Edge TPU runtime, "
                        "USB 3 connection, and that the model filename ends with '_edgetpu.tflite'."
                    ) from exc

                current = self.update_tracks(result, source_time_sec)
                current_ids = [tid for tid, _, _ in current]

                self.update_behavior(current_ids)
                self.cleanup_stale(source_time_sec)

                annotated = self.draw_video(frame, current, source_time_sec)
                panel = self.draw_panel(current_ids)
                display_frame = self.compose(annotated, panel)

                elapsed = time.perf_counter() - loop_t0
                self.update_fps(elapsed)

                self.recorder.write_frame(display_frame)

                cv2.imshow(self.window_name, display_frame)
                key = cv2.waitKey(1) & 0xFF

                if key in (27, ord("q")):
                    break
                if key == ord("r"):
                    self.recorder.toggle()

                self.frame_index += 1

        finally:
            self.recorder.stop()
            self.cap.release()
            cv2.destroyAllWindows()


def auto_find_one(pattern: str, roots: List[Path]) -> Optional[Path]:
    found: List[Path] = []
    for root in roots:
        if root.exists():
            found.extend(root.rglob(pattern))
    found = sorted(set(p.resolve() for p in found if p.is_file()))
    if len(found) == 1:
        return found[0]
    return None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Front fish demo on Raspberry Pi 4 + Coral Edge TPU."
    )

    p.add_argument(
        "--source",
        default="0",
        help="OpenCV camera index (e.g. 0) or video file path.",
    )
    p.add_argument(
        "--det-model",
        required=True,
        help="YOLO model. For Coral, keep filename ending '_edgetpu.tflite'.",
    )
    p.add_argument(
        "--tracker",
        default="configs/trackers/front_bytetrack_b15.yaml",
        help="Exact ByteTrack YAML selected by the research pipeline.",
    )
    p.add_argument(
        "--behavior-model",
        default="models/behavior/front_behavior_model.joblib",
    )
    p.add_argument(
        "--schema",
        default="results/behavior/front_behavior_feature_schema.json",
    )
    p.add_argument(
        "--metadata",
        default="models/behavior/front_behavior_model_metadata.json",
    )

    p.add_argument("--conf", type=float, default=0.50)
    p.add_argument("--iou", type=float, default=0.70)
    p.add_argument(
        "--imgsz",
        type=int,
        default=None,
        help="Normally omit for fixed-size EdgeTPU TFLite models.",
    )
    p.add_argument(
        "--tpu-device",
        default=None,
        help="Optional, e.g. tpu:0. Omit when using one Coral.",
    )

    p.add_argument("--camera-width", type=int, default=1280)
    p.add_argument("--camera-height", type=int, default=720)
    p.add_argument("--camera-fps", type=float, default=30.0)

    p.add_argument("--display-width", type=int, default=800)
    p.add_argument("--display-height", type=int, default=480)
    p.add_argument("--video-fraction", type=float, default=0.65)
    p.add_argument("--fullscreen", action="store_true")

    p.add_argument(
        "--output-dir",
        default="outputs/pi_front_demo",
    )
    p.add_argument("--record", action="store_true")
    p.add_argument("--record-fps", type=float, default=20.0)

    return p


def main() -> int:
    args = build_parser().parse_args()

    tracker_path = Path(args.tracker)
    if tracker_path.exists():
        args.tracker = str(tracker_path.resolve())
    elif args.tracker != "bytetrack.yaml":
        print(
            f"[WARN] Custom tracker YAML not found: {args.tracker}\n"
            "       Pass the exact front_bytetrack_b15.yaml from the project, "
            "or explicitly use --tracker bytetrack.yaml for a non-identical fallback."
        )

    app = FishMonitor(args)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
