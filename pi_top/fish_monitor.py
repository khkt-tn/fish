#!/usr/bin/env python3
"""CPU-only TOP-camera video demo: YOLO detection, ByteTrack, trajectory, and motion metrics."""

from __future__ import annotations

import argparse
import math
import os
import statistics
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Accepted TOP research configuration.
DEFAULT_MODEL = "runs/top/yolov8n_top_v2_baseline/weights/best.pt"
DEFAULT_TRACKER = "configs/trackers/top_bytetrack_b15.yaml"
DEFAULT_CONF = 0.50  # Tracking floor; ByteTrack high/new-track threshold remains 0.68.
DEFAULT_IOU = 0.70
DEFAULT_IMGSZ = 320
DEFAULT_MAX_DET = 20

WINDOW_SEC = 5.0
STEP_SEC = 1.0
MAX_INTERP_GAP_FRAMES = 3
SMOOTH_WINDOW_FRAMES = 5
FEATURE_LATENCY_FRAMES = 2
TAIL_SEC = 1.5
HISTORY_KEEP_SEC = 8.0

EXPECTED_TRACKER = {
    "tracker_type": "bytetrack",
    "track_high_thresh": 0.68,
    "track_low_thresh": 0.50,
    "new_track_thresh": 0.68,
    "track_buffer": 15,
    "match_thresh": 0.80,
    "fuse_score": True,
}

# Loaded only after CLI parsing so `--help` remains available before dependencies are installed.
cv2 = None
np = None
yaml = None
Image = None
ImageDraw = None
ImageFont = None


def load_runtime_dependencies() -> None:
    global cv2, np, yaml, Image, ImageDraw, ImageFont
    try:
        import cv2 as cv2_module
        import numpy as numpy_module
        import yaml as yaml_module
        from PIL import Image as image_module
        from PIL import ImageDraw as image_draw_module
        from PIL import ImageFont as image_font_module
    except ImportError as exc:
        raise RuntimeError(
            "Thiếu dependency cho demo. Chạy: python3 -m pip install -r "
            "pi_top/requirements_pi.txt"
        ) from exc

    cv2 = cv2_module
    np = numpy_module
    yaml = yaml_module
    Image = image_module
    ImageDraw = image_draw_module
    ImageFont = image_font_module


def resolve_existing_path(value: str, *, directory_ok: bool = False) -> Path:
    supplied = Path(value).expanduser()
    candidates = [supplied] if supplied.is_absolute() else [Path.cwd() / supplied, PROJECT_ROOT / supplied]
    checked: list[Path] = []
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in checked:
            continue
        checked.append(candidate)
        if candidate.is_file() or (directory_ok and candidate.is_dir()):
            return candidate
    rendered = ", ".join(str(path) for path in checked)
    raise FileNotFoundError(f"Không tìm thấy đường dẫn: {value}. Đã kiểm tra: {rendered}")


def configure_cpu_threads(requested: Optional[int]) -> int:
    threads = int(requested) if requested is not None else min(4, os.cpu_count() or 1)
    if threads < 1:
        raise ValueError("--threads phải >= 1")

    cv2.setNumThreads(threads)
    try:
        import torch

        torch.set_num_threads(threads)
        try:
            torch.set_num_interop_threads(max(1, min(2, threads)))
        except RuntimeError:
            # Inter-op threads may already be initialized by the runtime.
            pass
    except ImportError:
        pass
    return threads


def safe_mean(values: Any) -> float:
    array = np.asarray(values, dtype=float)
    finite = array[np.isfinite(array)]
    return float(np.mean(finite)) if len(finite) else float("nan")


def centered_rolling_median(values: Any, window: int = SMOOTH_WINDOW_FRAMES) -> Any:
    """Match rolling(window=5, center=True, min_periods=1).median()."""
    array = np.asarray(values, dtype=float)
    if len(array) == 0:
        return array.copy()
    effective = max(1, int(window))
    half = effective // 2
    output = np.empty(len(array), dtype=float)
    for index in range(len(array)):
        lo = max(0, index - half)
        hi = min(len(array), index + half + 1)
        output[index] = float(np.median(array[lo:hi]))
    return output


def wrap_to_pi(angle: Any) -> Any:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


@dataclass
class TrackSample:
    frame_index: int
    time_sec: float
    cx_raw: float
    cy_raw: float
    confidence: float
    observed: bool
    interpolated: bool


@dataclass
class MotionMetrics:
    feature_end_sec: float
    mean_speed_diag_s: float
    path_efficiency: float
    mean_abs_turn_rad: float


@dataclass
class TrackState:
    track_id: int
    frame_width: int
    frame_height: int
    fps_source: float
    samples: list[TrackSample] = field(default_factory=list)
    last_frame_index: Optional[int] = None
    last_seen_time_sec: Optional[float] = None
    segment_start_sec: Optional[float] = None
    segment_no: int = 1
    last_feature_end_sec: float = -1.0e12
    metrics: Optional[MotionMetrics] = None

    def reset_segment(self) -> None:
        self.samples.clear()
        self.last_frame_index = None
        self.last_seen_time_sec = None
        self.segment_start_sec = None
        self.segment_no += 1
        self.last_feature_end_sec = -1.0e12
        self.metrics = None

    def add_observation(
        self,
        frame_index: int,
        time_sec: float,
        xyxy: tuple[float, float, float, float],
        confidence: float,
    ) -> None:
        x1, y1, x2, y2 = map(float, xyxy)
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        if self.last_frame_index is not None and self.samples:
            frame_difference = int(frame_index - self.last_frame_index)
            missing_frames = frame_difference - 1
            if frame_difference <= 0 or missing_frames > MAX_INTERP_GAP_FRAMES:
                self.reset_segment()
            elif missing_frames > 0:
                previous = self.samples[-1]
                for offset in range(1, missing_frames + 1):
                    alpha = offset / float(frame_difference)
                    self.samples.append(
                        TrackSample(
                            frame_index=previous.frame_index + offset,
                            time_sec=previous.time_sec + alpha * (time_sec - previous.time_sec),
                            cx_raw=previous.cx_raw + alpha * (cx - previous.cx_raw),
                            cy_raw=previous.cy_raw + alpha * (cy - previous.cy_raw),
                            confidence=float("nan"),
                            observed=False,
                            interpolated=True,
                        )
                    )

        if self.segment_start_sec is None:
            self.segment_start_sec = float(time_sec)

        self.samples.append(
            TrackSample(
                frame_index=int(frame_index),
                time_sec=float(time_sec),
                cx_raw=float(cx),
                cy_raw=float(cy),
                confidence=float(confidence),
                observed=True,
                interpolated=False,
            )
        )
        self.last_frame_index = int(frame_index)
        self.last_seen_time_sec = float(time_sec)

        cutoff = float(time_sec) - HISTORY_KEEP_SEC
        if len(self.samples) > 10:
            self.samples = [sample for sample in self.samples if sample.time_sec >= cutoff]

    @property
    def segment_duration_sec(self) -> float:
        if self.segment_start_sec is None or self.last_seen_time_sec is None:
            return 0.0
        return max(0.0, float(self.last_seen_time_sec - self.segment_start_sec))

    def cleaned_arrays(self) -> Optional[dict[str, Any]]:
        if len(self.samples) < 2:
            return None
        ordered = sorted(self.samples, key=lambda sample: sample.frame_index)
        return {
            "frame_index": np.asarray([sample.frame_index for sample in ordered], dtype=int),
            "time_sec": np.asarray([sample.time_sec for sample in ordered], dtype=float),
            "cx_clean": centered_rolling_median([sample.cx_raw for sample in ordered]),
            "cy_clean": centered_rolling_median([sample.cy_raw for sample in ordered]),
        }

    def tail_points(self, now_sec: float) -> list[tuple[int, int]]:
        arrays = self.cleaned_arrays()
        if arrays is None:
            return []
        mask = arrays["time_sec"] >= float(now_sec) - TAIL_SEC
        return [
            (int(round(x)), int(round(y)))
            for x, y in zip(arrays["cx_clean"][mask], arrays["cy_clean"][mask])
        ]

    def compute_motion_metrics(self) -> Optional[MotionMetrics]:
        arrays = self.cleaned_arrays()
        if arrays is None or len(arrays["time_sec"]) < 3:
            return None

        count = len(arrays["time_sec"])
        latency = min(FEATURE_LATENCY_FRAMES, count - 1)
        eligible_index = count - 1 - latency
        frame_period = 1.0 / max(float(self.fps_source), 1.0e-9)
        feature_end = float(arrays["time_sec"][eligible_index]) + frame_period
        feature_start = feature_end - WINDOW_SEC

        # A complete five-second source-time window is mandatory for display.
        if float(arrays["time_sec"][0]) > feature_start + frame_period + 1.0e-9:
            return None

        mask = (arrays["time_sec"] >= feature_start) & (arrays["time_sec"] < feature_end)
        indices = np.flatnonzero(mask)
        if len(indices) < 3:
            return None

        times = arrays["time_sec"][indices]
        x_values = arrays["cx_clean"][indices]
        y_values = arrays["cy_clean"][indices]
        dt = np.diff(times)
        dx = np.diff(x_values)
        dy = np.diff(y_values)
        valid_dt = dt > 0
        if not valid_dt.any():
            return None

        steps = np.hypot(dx, dy)
        speeds = np.divide(
            steps,
            dt,
            out=np.full_like(steps, np.nan, dtype=float),
            where=valid_dt,
        )
        diagonal = math.hypot(float(self.frame_width), float(self.frame_height))
        normalized_speeds = speeds / diagonal if diagonal > 0 else np.full_like(speeds, np.nan)

        headings = np.full_like(steps, np.nan, dtype=float)
        moving = steps > 0
        headings[moving] = np.arctan2(dy[moving], dx[moving])
        turns = np.asarray(
            [
                wrap_to_pi(headings[index] - headings[index - 1])
                for index in range(1, len(headings))
                if np.isfinite(headings[index]) and np.isfinite(headings[index - 1])
            ],
            dtype=float,
        )

        path_length = float(np.sum(steps[np.isfinite(steps)]))
        net_displacement = float(math.hypot(x_values[-1] - x_values[0], y_values[-1] - y_values[0]))
        path_efficiency = net_displacement / path_length if path_length > 1.0e-9 else 0.0
        path_efficiency = min(1.0, max(0.0, float(path_efficiency)))

        return MotionMetrics(
            feature_end_sec=feature_end,
            mean_speed_diag_s=safe_mean(normalized_speeds),
            path_efficiency=path_efficiency,
            mean_abs_turn_rad=safe_mean(np.abs(turns)),
        )

    def update_metrics_if_due(self) -> None:
        candidate = self.compute_motion_metrics()
        if candidate is None:
            return
        if candidate.feature_end_sec - self.last_feature_end_sec < STEP_SEC - 1.0e-6:
            return
        self.metrics = candidate
        self.last_feature_end_sec = candidate.feature_end_sec


@dataclass(frozen=True)
class TrackedBox:
    track_id: int
    xyxy: tuple[float, float, float, float]
    confidence: float


class RollingPerformance:
    def __init__(self) -> None:
        self.inference_ms: deque[float] = deque(maxlen=120)
        self.pipeline_fps: deque[float] = deque(maxlen=120)

    @property
    def latest_inference_ms(self) -> float:
        return self.inference_ms[-1] if self.inference_ms else float("nan")

    @property
    def detector_fps(self) -> float:
        mean_ms = safe_mean(self.inference_ms)
        return 1000.0 / mean_ms if math.isfinite(mean_ms) and mean_ms > 0 else float("nan")

    @property
    def display_fps(self) -> float:
        return safe_mean(self.pipeline_fps)


class BenchmarkStats:
    def __init__(self, source_fps: float) -> None:
        self.source_fps = float(source_fps)
        self.frames_read = 0
        self.detector_calls = 0
        self.inference_ms: list[float] = []
        self.started = time.perf_counter()

    def report(self) -> None:
        runtime = max(time.perf_counter() - self.started, 1.0e-9)
        mean_ms = statistics.fmean(self.inference_ms) if self.inference_ms else float("nan")
        median_ms = statistics.median(self.inference_ms) if self.inference_ms else float("nan")
        detector_fps = 1000.0 / mean_ms if math.isfinite(mean_ms) and mean_ms > 0 else float("nan")
        overall_fps = self.frames_read / runtime
        print("\nBENCHMARK CPU TOP DEMO")
        print(f"Source FPS: {self.source_fps:.3f}")
        print(f"Frames read: {self.frames_read}")
        print(f"Detector calls: {self.detector_calls}")
        print(f"Mean inference ms: {mean_ms:.3f}")
        print(f"Median inference ms: {median_ms:.3f}")
        print(f"Detector FPS: {detector_fps:.3f}")
        print(f"Overall pipeline FPS: {overall_fps:.3f}")


def load_font(size: int) -> Any:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    raise RuntimeError(
        "Không tìm thấy font Unicode cho panel tiếng Việt. "
        "Trên Raspberry Pi OS, cài gói fonts-dejavu-core."
    )


def put_ascii_text(
    image: Any,
    text: str,
    position: tuple[int, int],
    scale: float = 0.55,
    thickness: int = 1,
    color: tuple[int, int, int] = (245, 245, 245),
) -> None:
    cv2.putText(
        image,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def fit_into(image: Any, width: int, height: int) -> Any:
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    source_height, source_width = image.shape[:2]
    scale = min(width / float(source_width), height / float(source_height))
    output_width = max(1, int(round(source_width * scale)))
    output_height = max(1, int(round(source_height * scale)))
    interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
    resized = cv2.resize(image, (output_width, output_height), interpolation=interpolation)
    left = (width - output_width) // 2
    top = (height - output_height) // 2
    canvas[top : top + output_height, left : left + output_width] = resized
    return canvas


class TopFishMonitor:
    def __init__(self, args: argparse.Namespace) -> None:
        from ultralytics import YOLO

        self.args = args
        self.source_path = resolve_existing_path(args.source)
        self.model_path = resolve_existing_path(args.det_model, directory_ok=True)
        self.tracker_path = resolve_existing_path(args.tracker)
        self._validate_tracker_config()

        self.threads = configure_cpu_threads(args.threads)
        self.detector = YOLO(str(self.model_path), task="detect")
        names = dict(self.detector.names)
        if 0 not in names or str(names[0]).strip().lower() not in {"ca", "cá", "fish"}:
            raise RuntimeError(f"Model không có class cá tại class ID 0: {names}")

        self.capture = cv2.VideoCapture(str(self.source_path))
        if not self.capture.isOpened():
            raise RuntimeError(f"Không mở được video: {self.source_path}")

        self.fps_source = float(self.capture.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(self.fps_source) or self.fps_source <= 1.0e-6:
            raise RuntimeError("Video không cung cấp source FPS hợp lệ")
        self.total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if self.frame_width <= 0 or self.frame_height <= 0:
            raise RuntimeError("Video không cung cấp kích thước khung hình hợp lệ")

        self.display_width = int(args.display_width)
        self.display_height = int(args.display_height)
        self.video_width = self.display_width if args.no_panel else int(round(self.display_width * 0.70))
        self.panel_width = self.display_width - self.video_width

        self.frame_index = 0
        self.last_source_time_sec = -1.0
        self.detect_every = int(args.detect_every)
        self.track_states: dict[int, TrackState] = {}
        self.visible_tracks: list[TrackedBox] = []
        self.performance = RollingPerformance()
        self.benchmark = BenchmarkStats(self.fps_source)
        self.tracker_runtime_checked = False
        self.paused = False
        self.fullscreen = bool(args.fullscreen and not args.benchmark)
        self.window_name = "Fish AI - Camera Top"
        self.last_display = None
        self.playback_source_anchor: Optional[float] = None
        self.playback_wall_anchor: Optional[float] = None

        self.font_title = load_font(16) if not args.no_panel and not args.benchmark else None
        self.font_body = load_font(12) if not args.no_panel and not args.benchmark else None
        self.font_small = load_font(10) if not args.no_panel and not args.benchmark else None

    def _validate_tracker_config(self) -> None:
        config = yaml.safe_load(self.tracker_path.read_text(encoding="utf-8"))
        if config != EXPECTED_TRACKER:
            raise RuntimeError(
                "Tracker YAML khác cấu hình TOP ByteTrack B15 đã chấp nhận. "
                f"Nhận được: {config}"
            )

    def _validate_runtime_tracker(self) -> None:
        if self.tracker_runtime_checked:
            return
        predictor = getattr(self.detector, "predictor", None)
        trackers = getattr(predictor, "trackers", None)
        if not trackers:
            raise RuntimeError("Không đọc được ByteTrack runtime sau lần suy luận đầu tiên")
        tracker_args = trackers[0].args
        actual = {key: getattr(tracker_args, key) for key in EXPECTED_TRACKER}
        if actual != EXPECTED_TRACKER:
            raise RuntimeError(f"ByteTrack runtime khác cấu hình yêu cầu: {actual}")
        self.tracker_runtime_checked = True

    def source_time_sec(self) -> float:
        position_ms = float(self.capture.get(cv2.CAP_PROP_POS_MSEC))
        fallback = self.frame_index / self.fps_source
        candidate = position_ms / 1000.0 if math.isfinite(position_ms) and position_ms >= 0 else fallback
        if self.frame_index > 0 and candidate <= self.last_source_time_sec:
            candidate = fallback
        self.last_source_time_sec = float(candidate)
        return float(candidate)

    def reset_tracking(self, reason: str) -> None:
        predictor = getattr(self.detector, "predictor", None)
        for tracker in getattr(predictor, "trackers", []) or []:
            tracker.reset()
        self.track_states.clear()
        self.visible_tracks = []
        self.tracker_runtime_checked = False
        print(f"[RESET] ByteTrack/history: {reason}")

    def rewind_video(self) -> None:
        if not self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0):
            self.capture.release()
            self.capture = cv2.VideoCapture(str(self.source_path))
            if not self.capture.isOpened():
                raise RuntimeError(f"Không thể mở lại video: {self.source_path}")
        self.frame_index = 0
        self.last_source_time_sec = -1.0
        self.playback_source_anchor = None
        self.playback_wall_anchor = None
        self.reset_tracking("video loop về frame đầu")

    def run_detector(self, frame: Any, source_time_sec: float) -> None:
        started = time.perf_counter()
        result = self.detector.track(
            source=frame,
            persist=True,
            tracker=str(self.tracker_path),
            conf=float(self.args.conf),
            iou=float(self.args.iou),
            imgsz=int(self.args.imgsz),
            max_det=int(self.args.max_det),
            classes=[0],
            device="cpu",
            verbose=False,
            save=False,
            show=False,
        )[0]
        detector_wall_ms = (time.perf_counter() - started) * 1000.0
        self._validate_runtime_tracker()

        inference_value = (getattr(result, "speed", None) or {}).get("inference")
        inference_ms = float(inference_value) if inference_value is not None else detector_wall_ms
        self.performance.inference_ms.append(inference_ms)
        self.benchmark.detector_calls += 1
        self.benchmark.inference_ms.append(inference_ms)

        tracked: list[TrackedBox] = []
        boxes = result.boxes
        if boxes is not None and boxes.id is not None and len(boxes) > 0:
            xyxy_values = boxes.xyxy.detach().cpu().numpy()
            track_ids = boxes.id.detach().cpu().numpy().astype(int)
            confidences = boxes.conf.detach().cpu().numpy().astype(float)
            classes = boxes.cls.detach().cpu().numpy().astype(int)
            for coordinates, track_id, confidence, class_id in zip(
                xyxy_values, track_ids, confidences, classes
            ):
                if int(class_id) != 0:
                    continue
                xyxy = tuple(map(float, coordinates.tolist()))
                tracked_box = TrackedBox(int(track_id), xyxy, float(confidence))
                tracked.append(tracked_box)

                state = self.track_states.get(int(track_id))
                if state is None:
                    state = TrackState(
                        track_id=int(track_id),
                        frame_width=self.frame_width,
                        frame_height=self.frame_height,
                        fps_source=self.fps_source,
                    )
                    self.track_states[int(track_id)] = state
                state.add_observation(self.frame_index, source_time_sec, xyxy, float(confidence))
                state.update_metrics_if_due()

        self.visible_tracks = tracked

    def draw_video(self, frame: Any, source_time_sec: float) -> None:
        height, width = frame.shape[:2]
        for tracked in self.visible_tracks:
            x1, y1, x2, y2 = tracked.xyxy
            left = max(0, min(width - 1, int(round(x1))))
            top = max(0, min(height - 1, int(round(y1))))
            right = max(0, min(width - 1, int(round(x2))))
            bottom = max(0, min(height - 1, int(round(y2))))
            center = (int(round((left + right) / 2.0)), int(round((top + bottom) / 2.0)))

            cv2.rectangle(frame, (left, top), (right, bottom), (40, 220, 70), 2)
            cv2.circle(frame, center, 4, (30, 220, 255), -1, cv2.LINE_AA)
            put_ascii_text(
                frame,
                f"Track ID {tracked.track_id} | conf {tracked.confidence:.2f}",
                (left, max(24, top - 8)),
                scale=0.58,
                thickness=2,
            )

            state = self.track_states.get(tracked.track_id)
            points = state.tail_points(source_time_sec) if state is not None else []
            if len(points) >= 2:
                cv2.polylines(
                    frame,
                    [np.asarray(points, dtype=np.int32)],
                    False,
                    (255, 210, 40),
                    2,
                    cv2.LINE_AA,
                )

        put_ascii_text(frame, "CAMERA TOP", (14, 30), scale=0.75, thickness=2)
        if self.args.no_panel:
            put_ascii_text(
                frame,
                f"Detection stride: {self.detect_every}",
                (14, 56),
                scale=0.55,
                thickness=1,
            )

    def draw_panel(self, source_time_sec: float) -> Any:
        panel = Image.new("RGB", (self.panel_width, self.display_height), (13, 20, 29))
        draw = ImageDraw.Draw(panel)
        white = (240, 244, 248)
        muted = (170, 184, 198)
        accent = (74, 222, 128)
        cyan = (56, 189, 248)

        x = 9
        y = 8
        draw.text((x, y), "FISH AI - CAMERA TOP", font=self.font_title, fill=white)
        y += 25
        inference_ms = self.performance.latest_inference_ms
        detector_fps = self.performance.detector_fps
        pipeline_fps = self.performance.display_fps
        header_lines = [
            "Model: YOLOv8n TOP",
            "Thiết bị: CPU",
            f"Kích thước suy luận: {self.args.imgsz}",
            f"Detection stride: {self.detect_every}",
            f"Thời gian suy luận NN: {inference_ms:.1f} ms"
            if math.isfinite(inference_ms)
            else "Thời gian suy luận NN: -- ms",
            f"FPS detector: {detector_fps:.1f}" if math.isfinite(detector_fps) else "FPS detector: --",
            f"FPS pipeline/display: {pipeline_fps:.1f}" if math.isfinite(pipeline_fps) else "FPS pipeline/display: --",
            f"Đối tượng đang theo dõi: {len(self.visible_tracks)}",
        ]
        for index, line in enumerate(header_lines):
            color = accent if index == len(header_lines) - 1 else muted
            draw.text((x, y), line, font=self.font_body, fill=color)
            y += 16

        draw.line((7, y + 1, self.panel_width - 7, y + 1), fill=(55, 70, 84), width=1)
        y += 8
        footer_top = self.display_height - 53
        row_height = 58
        capacity = max(1, (footer_top - y) // row_height)
        active_ids = sorted(tracked.track_id for tracked in self.visible_tracks)
        if len(active_ids) > capacity:
            start = int(source_time_sec // 2.0) % len(active_ids)
            active_ids = [active_ids[(start + offset) % len(active_ids)] for offset in range(capacity)]

        for track_id in active_ids:
            state = self.track_states[track_id]
            draw.text((x, y), f"ID {track_id}", font=self.font_body, fill=cyan)
            y += 13
            draw.text(
                (x + 4, y),
                f"Thời lượng đoạn: {state.segment_duration_sec:.1f} s",
                font=self.font_small,
                fill=muted,
            )
            y += 12
            metrics = state.metrics
            if metrics is None:
                draw.text((x + 4, y), "Đang thu dữ liệu...", font=self.font_body, fill=(250, 204, 21))
                y += 33
                continue

            speed = (
                f"{metrics.mean_speed_diag_s:.3f}"
                if math.isfinite(metrics.mean_speed_diag_s)
                else "--"
            )
            turning = (
                f"{metrics.mean_abs_turn_rad:.3f}"
                if math.isfinite(metrics.mean_abs_turn_rad)
                else "--"
            )
            draw.text((x + 4, y), f"Tốc độ: {speed} diag/s", font=self.font_small, fill=white)
            y += 11
            draw.text(
                (x + 4, y),
                f"Hiệu quả đường đi: {metrics.path_efficiency:.3f}",
                font=self.font_small,
                fill=white,
            )
            y += 11
            draw.text((x + 4, y), f"Đổi hướng: {turning} rad", font=self.font_small, fill=white)
            y += 11

        draw.line((7, footer_top, self.panel_width - 7, footer_top), fill=(55, 70, 84), width=1)
        draw.text((x, footer_top + 4), "ID = mã theo dõi, không phải", font=self.font_small, fill=muted)
        draw.text((x, footer_top + 15), "danh tính sinh học", font=self.font_small, fill=muted)
        draw.text((x, footer_top + 29), "Các đại lượng được chuẩn hóa", font=self.font_small, fill=muted)
        draw.text((x, footer_top + 40), "theo khung hình", font=self.font_small, fill=muted)

        rgb = np.asarray(panel)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    def compose_display(self, frame: Any, source_time_sec: float) -> Any:
        self.draw_video(frame, source_time_sec)
        video = fit_into(frame, self.video_width, self.display_height)
        if self.args.no_panel:
            return video
        panel = self.draw_panel(source_time_sec)
        return np.hstack((video, panel))

    def apply_fullscreen(self) -> None:
        mode = cv2.WINDOW_FULLSCREEN if self.fullscreen else cv2.WINDOW_NORMAL
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, mode)
        if not self.fullscreen:
            cv2.resizeWindow(self.window_name, self.display_width, self.display_height)

    def handle_key(self, key: int) -> bool:
        if key in (27, ord("q")):
            return False
        if key == ord(" "):
            self.paused = not self.paused
            if not self.paused:
                self.playback_source_anchor = self.last_source_time_sec
                self.playback_wall_anchor = time.perf_counter()
            print("[PAUSE]" if self.paused else "[RESUME]")
        elif key == ord("r"):
            self.reset_tracking("phím r")
        elif key == ord("f"):
            self.fullscreen = not self.fullscreen
            self.apply_fullscreen()
        elif key in (ord("1"), ord("2"), ord("3")):
            self.detect_every = int(chr(key))
            print(f"[CONFIG] Detection stride: {self.detect_every}")
        return True

    def pace_video(self, source_time_sec: float) -> None:
        if self.args.benchmark:
            return
        if self.playback_source_anchor is None or self.playback_wall_anchor is None:
            self.playback_source_anchor = float(source_time_sec)
            self.playback_wall_anchor = time.perf_counter()
            return
        target = self.playback_wall_anchor + (source_time_sec - self.playback_source_anchor)
        delay = target - time.perf_counter()
        if delay > 0:
            time.sleep(delay)

    def print_startup(self) -> None:
        print("FISH AI - CAMERA TOP | CPU video demo")
        print(f"Source: {self.source_path}")
        print(f"Source FPS: {self.fps_source:.3f}")
        print(f"Frames: {self.total_frames}")
        print(f"Resolution: {self.frame_width}x{self.frame_height}")
        print(f"Model: {self.model_path}")
        print(f"Tracker: {self.tracker_path}")
        print(f"imgsz={self.args.imgsz}, conf={self.args.conf:.2f}, iou={self.args.iou:.2f}")
        print(f"Detection stride: {self.detect_every}")
        print(f"CPU threads: {self.threads}")
        if not self.args.benchmark:
            print("Phím: q/ESC thoát | SPACE pause/resume | r reset | f fullscreen | 1/2/3 stride")

    def run(self) -> None:
        self.print_startup()
        if self.args.benchmark and self.args.loop_video:
            print("[INFO] --loop-video được bỏ qua trong benchmark để benchmark có điểm dừng.")

        if not self.args.benchmark:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, self.display_width, self.display_height)
            self.apply_fullscreen()

        keep_running = True
        try:
            while keep_running:
                if self.paused and not self.args.benchmark:
                    if self.last_display is not None:
                        cv2.imshow(self.window_name, self.last_display)
                    keep_running = self.handle_key(cv2.waitKey(30) & 0xFF)
                    continue

                loop_started = time.perf_counter()
                ok, frame = self.capture.read()
                if not ok:
                    if self.args.loop_video and not self.args.benchmark:
                        self.rewind_video()
                        continue
                    break

                self.benchmark.frames_read += 1
                height, width = frame.shape[:2]
                if (width, height) != (self.frame_width, self.frame_height):
                    self.frame_width, self.frame_height = int(width), int(height)
                    for state in self.track_states.values():
                        state.frame_width = int(width)
                        state.frame_height = int(height)

                timestamp = self.source_time_sec()
                if self.frame_index % self.detect_every == 0:
                    self.run_detector(frame, timestamp)

                if not self.args.benchmark:
                    display = self.compose_display(frame, timestamp)
                    self.pace_video(timestamp)
                    elapsed = max(time.perf_counter() - loop_started, 1.0e-9)
                    self.performance.pipeline_fps.append(1.0 / elapsed)
                    self.last_display = display
                    cv2.imshow(self.window_name, display)
                    keep_running = self.handle_key(cv2.waitKey(1) & 0xFF)

                self.frame_index += 1
        finally:
            self.capture.release()
            if not self.args.benchmark:
                cv2.destroyAllWindows()

        if self.args.benchmark:
            self.benchmark.report()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Demo CPU CAMERA TOP từ video: YOLOv8n TOP -> ByteTrack -> quỹ đạo -> chỉ số 5 giây.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--source", required=True, help="Đường dẫn video TOP có sẵn.")
    parser.add_argument(
        "--det-model",
        default=DEFAULT_MODEL,
        help="File best.pt hoặc thư mục model NCNN đã có sẵn.",
    )
    parser.add_argument("--tracker", default=DEFAULT_TRACKER, help="Cấu hình ByteTrack TOP B15.")
    parser.add_argument("--imgsz", type=int, choices=(320, 416, 512, 640), default=DEFAULT_IMGSZ)
    parser.add_argument("--detect-every", type=int, default=1, metavar="N")
    parser.add_argument("--max-det", type=int, default=DEFAULT_MAX_DET)
    parser.add_argument("--conf", type=float, default=DEFAULT_CONF)
    parser.add_argument("--iou", type=float, default=DEFAULT_IOU)
    parser.add_argument("--display-width", type=int, default=800)
    parser.add_argument("--display-height", type=int, default=480)
    parser.add_argument("--threads", type=int, default=None, help="Số CPU thread; mặc định min(4, os.cpu_count()).")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--loop-video", action="store_true")
    parser.add_argument("--no-panel", action="store_true", help="Ẩn panel để giảm chi phí render.")
    parser.add_argument("--benchmark", action="store_true", help="Chạy headless đến cuối video và in thống kê CPU.")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.detect_every < 1:
        raise ValueError("--detect-every phải >= 1")
    if args.max_det < 1:
        raise ValueError("--max-det phải >= 1")
    if not 0.0 <= args.conf <= 1.0:
        raise ValueError("--conf phải nằm trong [0, 1]")
    if not 0.0 <= args.iou <= 1.0:
        raise ValueError("--iou phải nằm trong [0, 1]")
    if args.display_width < 400 or args.display_height < 240:
        raise ValueError("Kích thước display tối thiểu là 400x240")
    if args.threads is not None and args.threads < 1:
        raise ValueError("--threads phải >= 1")


def main() -> int:
    args = build_parser().parse_args()
    validate_args(args)
    load_runtime_dependencies()
    TopFishMonitor(args).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
