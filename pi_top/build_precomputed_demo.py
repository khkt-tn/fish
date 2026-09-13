#!/usr/bin/env python3
"""Render the accepted TOP research artifacts into a Pi-friendly demo video.

This script is intentionally a research-machine tool.  It reads the source TOP
video, raw ByteTrack CSV, cleaned trajectories, and precomputed TOP feature
windows.  It never imports or runs YOLO, Torch, Ultralytics, ByteTrack, or a
behavior model.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480
PANEL_WIDTH = 240
VIDEO_WIDTH = DISPLAY_WIDTH - PANEL_WIDTH
TAIL_SEC = 1.5
WINDOW_SEC = 5.0
MIN_WINDOW_COVERAGE = 0.6


def load_dependencies() -> tuple[Any, Any, Any]:
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(
            "Cần chạy script trong environment fish có opencv-python, numpy và Pillow."
        ) from exc
    return cv2, np, (Image, ImageDraw, ImageFont)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render video demo TOP từ tracking/trajectory/behavior artifacts đã có."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video-id", choices=("1", "2"), help="Render một video TOP.")
    group.add_argument("--all", action="store_true", help="Render cả TOP video 1 và 2.")
    parser.add_argument(
        "--output-dir", default="pi_top/demo", help="Thư mục chứa top_demo_<id>.mp4."
    )
    parser.add_argument(
        "--qa-dir",
        default="artifacts_local/pi_top_precomputed_demo_qa",
        help="Thư mục lưu screenshot và qa_report.json.",
    )
    parser.add_argument(
        "--no-package",
        action="store_true",
        help="Không tạo artifacts_local/pi_top_precomputed_demo.tar.gz.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str | None) -> float:
    if value is None or value == "":
        return float("nan")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def as_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def finite(value: float) -> bool:
    return math.isfinite(value)


def find_font(ImageFont: Any, size: int) -> Any:
    candidates = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    )
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def parse_tracker_rows(rows: list[dict[str, str]]) -> dict[int, list[dict[str, Any]]]:
    by_frame: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        frame_index = as_int(row.get("frame_index"))
        track_id = as_int(row.get("track_id"))
        if frame_index is None or track_id is None:
            continue
        coords = [as_float(row.get(key)) for key in ("x1", "y1", "x2", "y2")]
        if not all(finite(value) for value in coords):
            continue
        by_frame[frame_index].append(
            {
                "frame_index": frame_index,
                "track_id": track_id,
                "confidence": as_float(row.get("confidence")),
                "bbox": tuple(coords),
                "time_sec": as_float(row.get("time_sec")),
            }
        )
    for frame_rows in by_frame.values():
        frame_rows.sort(key=lambda item: item["track_id"])
    return by_frame


def parse_clean_rows(
    rows: list[dict[str, str]], video_id: str
) -> tuple[dict[tuple[int, int], list[dict[str, Any]]], dict[str, list[dict[str, Any]]], dict[str, float]]:
    by_key: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    by_uid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    segment_starts: dict[str, float] = {}
    for row in rows:
        if row.get("video_id") != video_id:
            continue
        frame_index = as_int(row.get("frame_index"))
        track_id = as_int(row.get("track_id"))
        uid = row.get("trajectory_uid", "")
        if frame_index is None or track_id is None or not uid:
            continue
        point = {
            "frame_index": frame_index,
            "track_id": track_id,
            "time_sec": as_float(row.get("time_sec")),
            "uid": uid,
            "cx": as_float(row.get("cx_clean")),
            "cy": as_float(row.get("cy_clean")),
            "interpolated": row.get("interpolated", "False").lower() == "true",
            "segment_start_sec": as_float(row.get("segment_start_sec")),
            "segment_end_sec": as_float(row.get("segment_end_sec")),
        }
        by_key[(frame_index, track_id)].append(point)
        by_uid[uid].append(point)
        if finite(point["segment_start_sec"]):
            segment_starts[uid] = point["segment_start_sec"]
    for points in by_uid.values():
        points.sort(key=lambda item: item["frame_index"])
    return by_key, by_uid, segment_starts


def parse_feature_rows(rows: list[dict[str, str]], video_id: str) -> dict[str, list[dict[str, Any]]]:
    by_uid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("video_id") != video_id or not row.get("trajectory_uid"):
            continue
        parsed: dict[str, Any] = dict(row)
        for key in (
            "window_start_sec",
            "window_end_sec",
            "coverage_ratio",
            "mean_speed_diag_s",
            "path_efficiency",
            "mean_abs_turn_rad",
            "window_time_span_sec",
        ):
            parsed[key] = as_float(row.get(key))
        if parsed["coverage_ratio"] >= MIN_WINDOW_COVERAGE:
            by_uid[row["trajectory_uid"]].append(parsed)
    for features in by_uid.values():
        features.sort(key=lambda item: item["window_end_sec"])
    return by_uid


def choose_feature(features: list[dict[str, Any]], source_time_sec: float) -> dict[str, Any] | None:
    selected = None
    for feature in features:
        end = feature["window_end_sec"]
        if finite(end) and end <= source_time_sec + 1e-6:
            selected = feature
        else:
            break
    return selected


def fit_video(frame: Any, width: int, height: int, cv2: Any, np: Any) -> Any:
    source_h, source_w = frame.shape[:2]
    scale = min(width / source_w, height / source_h)
    resized_w = max(1, int(round(source_w * scale)))
    resized_h = max(1, int(round(source_h * scale)))
    resized = cv2.resize(frame, (resized_w, resized_h), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    left = (width - resized_w) // 2
    top = (height - resized_h) // 2
    canvas[top : top + resized_h, left : left + resized_w] = resized
    return canvas


def draw_panel(
    panel: Any,
    *,
    source_time_sec: float,
    duration_sec: float,
    active: list[dict[str, Any]],
    feature_by_uid: dict[str, list[dict[str, Any]]],
    uid_by_key: dict[tuple[int, int], list[dict[str, Any]]],
    segment_starts: dict[str, float],
    Image: Any,
    ImageDraw: Any,
    ImageFont: Any,
) -> Any:
    image = Image.fromarray(panel[:, :, ::-1])
    draw = ImageDraw.Draw(image)
    title = find_font(ImageFont, 16)
    body = find_font(ImageFont, 12)
    small = find_font(ImageFont, 10)
    white = (240, 244, 248)
    muted = (170, 184, 198)
    accent = (74, 222, 128)
    cyan = (56, 189, 248)
    yellow = (250, 204, 21)
    x, y = 8, 8
    draw.text((x, y), "FISH AI - CAMERA TOP", font=title, fill=white)
    y += 23
    draw.text((x, y), "Nguồn: Video thí nghiệm", font=body, fill=muted)
    y += 16
    draw.text((x, y), "Phân tích: YOLOv8n TOP + ByteTrack", font=small, fill=muted)
    y += 14
    draw.text((x, y), f"Thời gian video: {source_time_sec:.1f}/{duration_sec:.1f} s", font=small, fill=muted)
    y += 14
    draw.text((x, y), f"Đối tượng đang theo dõi: {len(active)}", font=body, fill=accent)
    y += 18
    draw.line((7, y, PANEL_WIDTH - 7, y), fill=(55, 70, 84), width=1)
    y += 6

    # At 240 px wide the panel can show a compact subset, while all metrics in
    # the rendered video remain source-time aligned.  The video itself carries
    # every bbox and tail, so no track is silently promoted to an identity.
    row_height = 72
    footer_top = DISPLAY_HEIGHT - 72
    capacity = max(1, (footer_top - y) // row_height)
    shown = active[:capacity]
    for item in shown:
        track_id = item["track_id"]
        draw.text((x, y), f"ID / mã theo dõi: {track_id}", font=body, fill=cyan)
        y += 14
        uid_rows = uid_by_key.get((item["frame_index"], track_id), [])
        uid = uid_rows[0]["uid"] if uid_rows else None
        elapsed = "--"
        if uid:
            start = segment_starts.get(uid, float("nan"))
            if finite(start):
                elapsed = f"{max(0.0, source_time_sec - start):.1f} s"
        draw.text((x + 3, y), f"Thời lượng đoạn quỹ đạo: {elapsed}", font=small, fill=muted)
        y += 12
        feature = choose_feature(feature_by_uid.get(uid, []), source_time_sec) if uid else None
        if feature is None:
            draw.text((x + 3, y), "Đang thu dữ liệu...", font=body, fill=yellow)
            y += 16
        else:
            values = (
                ("Tốc độ", feature["mean_speed_diag_s"], "diag/s"),
                ("Hiệu quả đường đi", feature["path_efficiency"], ""),
                ("Đổi hướng", feature["mean_abs_turn_rad"], "rad"),
            )
            for label, value, unit in values:
                rendered = f"{value:.3f} {unit}".rstrip() if finite(value) else "--"
                draw.text((x + 3, y), f"{label}: {rendered}", font=small, fill=white)
                y += 11
        y += 4

    draw.line((7, footer_top, PANEL_WIDTH - 7, footer_top), fill=(55, 70, 84), width=1)
    footer = (
        "ID = mã theo dõi, không phải",
        "danh tính sinh học",
        "Các đại lượng được chuẩn hóa",
        "theo khung hình",
        "Kết quả AI được xử lý trước",
        "từ video thí nghiệm",
    )
    fy = footer_top + 4
    for line in footer:
        draw.text((x, fy), line, font=small, fill=muted)
        fy += 13
    return image.convert("RGB")


def compose_frame(
    frame: Any,
    *,
    frame_index: int,
    source_time_sec: float,
    duration_sec: float,
    active: list[dict[str, Any]],
    uid_by_key: dict[tuple[int, int], list[dict[str, Any]]],
    points_by_uid: dict[str, list[dict[str, Any]]],
    feature_by_uid: dict[str, list[dict[str, Any]]],
    segment_starts: dict[str, float],
    cv2: Any,
    np: Any,
    Image: Any,
    ImageDraw: Any,
    ImageFont: Any,
) -> Any:
    height, width = frame.shape[:2]
    canvas = frame.copy()
    colors = ((54, 220, 90), (40, 190, 240), (240, 180, 40), (200, 90, 220))
    for index, item in enumerate(active):
        x1, y1, x2, y2 = item["bbox"]
        left = max(0, min(width - 1, int(round(x1))))
        top = max(0, min(height - 1, int(round(y1))))
        right = max(0, min(width - 1, int(round(x2))))
        bottom = max(0, min(height - 1, int(round(y2))))
        color = colors[index % len(colors)]
        cv2.rectangle(canvas, (left, top), (right, bottom), color, 2, cv2.LINE_AA)
        center = ((left + right) // 2, (top + bottom) // 2)
        cv2.circle(canvas, center, 4, (30, 220, 255), -1, cv2.LINE_AA)
        uid_rows = uid_by_key.get((frame_index, item["track_id"]), [])
        uid = uid_rows[0]["uid"] if uid_rows else None
        if uid:
            points = [
                point
                for point in points_by_uid.get(uid, [])
                if point["frame_index"] <= frame_index
                and point["time_sec"] >= source_time_sec - TAIL_SEC
                and finite(point["cx"])
                and finite(point["cy"])
            ]
            if len(points) >= 2:
                polyline = np.asarray([(round(p["cx"]), round(p["cy"])) for p in points], dtype=np.int32)
                cv2.polylines(canvas, [polyline], False, (255, 210, 40), 2, cv2.LINE_AA)

    # Pillow is used for all display text so Vietnamese glyphs render correctly.
    image = Image.fromarray(canvas[:, :, ::-1])
    draw = ImageDraw.Draw(image)
    label_font = find_font(ImageFont, 14)
    small_font = find_font(ImageFont, 11)
    draw.text((12, 10), "CAMERA TOP", font=label_font, fill=(245, 245, 245))
    for item in active:
        x1, y1, _, _ = item["bbox"]
        uid_rows = uid_by_key.get((frame_index, item["track_id"]), [])
        uid = uid_rows[0]["uid"] if uid_rows else None
        confidence = item["confidence"]
        label = f"ID {item['track_id']}"
        if finite(confidence):
            label += f" | conf {confidence:.2f}"
        tx, ty = max(0, int(round(x1))), max(18, int(round(y1)) - 17)
        draw.rectangle((tx, ty - 1, tx + 120, ty + 15), fill=(10, 30, 40))
        draw.text((tx + 2, ty), label, font=small_font, fill=(245, 245, 245))

    video = fit_video(np.asarray(image)[:, :, ::-1], VIDEO_WIDTH, DISPLAY_HEIGHT, cv2, np)
    panel = np.zeros((DISPLAY_HEIGHT, PANEL_WIDTH, 3), dtype=np.uint8)
    panel[:, :] = (13, 20, 29)
    panel_image = draw_panel(
        panel,
        source_time_sec=source_time_sec,
        duration_sec=duration_sec,
        active=active,
        feature_by_uid=feature_by_uid,
        uid_by_key=uid_by_key,
        segment_starts=segment_starts,
        Image=Image,
        ImageDraw=ImageDraw,
        ImageFont=ImageFont,
    )
    panel = np.asarray(panel_image)[:, :, ::-1].copy()
    return np.hstack((video, panel))


def ffprobe_json(path: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        return {}
    command = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,pix_fmt,width,height,avg_frame_rate,nb_frames,duration",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return {}
    try:
        payload = json.loads(result.stdout)
        streams = payload.get("streams", [])
        return streams[0] if streams else {}
    except json.JSONDecodeError:
        return {}


def parse_rate(value: str | None) -> float:
    if not value:
        return float("nan")
    try:
        if "/" in value:
            numerator, denominator = value.split("/", 1)
            return float(numerator) / float(denominator)
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return float("nan")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def encode_h264(intermediate: Path, output: Path) -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        intermediate.replace(output)
        return "opencv-mp4v (ffmpeg unavailable)"
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(intermediate),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        fallback = command.copy()
        fallback[fallback.index("libx264")] = "h264"
        result = subprocess.run(fallback, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg encode thất bại cho {output}: {result.stderr[-1000:]}")
    intermediate.unlink(missing_ok=True)
    metadata = ffprobe_json(output)
    codec = metadata.get("codec_name", "unknown")
    pixel_format = metadata.get("pix_fmt", "unknown")
    return f"{codec}/{pixel_format}"


def render_video(video_id: str, output_dir: Path, qa_dir: Path, cv2: Any, np: Any, pil: tuple[Any, Any, Any]) -> dict[str, Any]:
    Image, ImageDraw, ImageFont = pil
    source = PROJECT_ROOT / "data" / "raw" / "top" / f"{video_id}.mp4"
    video_key = f"TOP_VIDEO_{video_id}"
    raw_path = PROJECT_ROOT / "outputs" / "top" / "tracking" / f"{video_id}_tracking_raw.csv"
    clean_path = PROJECT_ROOT / "outputs" / "top" / "trajectory" / "top_cleaned_trajectories.csv"
    feature_path = PROJECT_ROOT / "outputs" / "top" / "behavior" / "top_individual_window_features.csv"
    for path in (source, raw_path, clean_path, feature_path):
        if not path.is_file():
            raise FileNotFoundError(f"Thiếu artifact TOP bắt buộc: {path}")

    raw_rows = read_csv(raw_path)
    clean_rows = read_csv(clean_path)
    feature_rows = read_csv(feature_path)
    by_frame = parse_tracker_rows(raw_rows)
    uid_by_key, points_by_uid, segment_starts = parse_clean_rows(clean_rows, video_key)
    feature_by_uid = parse_feature_rows(feature_rows, video_key)
    if not by_frame or not points_by_uid:
        raise RuntimeError(f"Không có tracking/trajectory hợp lệ cho {video_key}")

    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise RuntimeError(f"Không thể mở video nguồn: {source}")
    source_fps = float(capture.get(cv2.CAP_PROP_FPS))
    if not finite(source_fps) or source_fps <= 0:
        source_fps = next(
            (as_float(row.get("fps_source")) for row in clean_rows if row.get("video_id") == video_key and finite(as_float(row.get("fps_source")))),
            1.0,
        )
    source_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    source_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    source_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = (source_frames - 1) / source_fps if source_frames > 0 else 0.0
    output_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"top_demo_{video_id}.mp4"
    temp_dir = Path(tempfile.mkdtemp(prefix=f"top_demo_{video_id}_", dir=str(qa_dir)))
    intermediate = temp_dir / "intermediate.mp4"
    writer = cv2.VideoWriter(
        str(intermediate), cv2.VideoWriter_fourcc(*"mp4v"), source_fps, (DISPLAY_WIDTH, DISPLAY_HEIGHT)
    )
    if not writer.isOpened():
        capture.release()
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Không mở được VideoWriter: {intermediate}")

    started = time.perf_counter()
    screenshots: dict[str, Path] = {}
    screenshot_targets = {"start": 0.0, "10s": 10.0, "middle": duration_sec / 2.0}
    rendered = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frame_index = rendered
            source_time_sec = frame_index / source_fps
            active = by_frame.get(frame_index, [])
            composed = compose_frame(
                frame,
                frame_index=frame_index,
                source_time_sec=source_time_sec,
                duration_sec=duration_sec,
                active=active,
                uid_by_key=uid_by_key,
                points_by_uid=points_by_uid,
                feature_by_uid=feature_by_uid,
                segment_starts=segment_starts,
                cv2=cv2,
                np=np,
                Image=Image,
                ImageDraw=ImageDraw,
                ImageFont=ImageFont,
            )
            writer.write(composed)
            for name, target in screenshot_targets.items():
                if name not in screenshots and source_time_sec >= target:
                    screenshot = qa_dir / f"top_demo_{video_id}_{name}.png"
                    cv2.imwrite(str(screenshot), composed)
                    screenshots[name] = screenshot
            rendered += 1
            if rendered % 200 == 0:
                elapsed = max(time.perf_counter() - started, 1e-9)
                print(f"[{video_id}] frame {rendered}/{source_frames} | {rendered / elapsed:.1f} render fps")
    finally:
        writer.release()
        capture.release()
    codec = encode_h264(intermediate, output)
    shutil.rmtree(temp_dir, ignore_errors=True)
    metadata = ffprobe_json(output)
    output_fps = parse_rate(metadata.get("avg_frame_rate"))
    output_duration = as_float(metadata.get("duration"))
    report = {
        "video_id": video_id,
        "source": str(source.relative_to(PROJECT_ROOT)),
        "raw_tracking": str(raw_path.relative_to(PROJECT_ROOT)),
        "cleaned_trajectory": str(clean_path.relative_to(PROJECT_ROOT)),
        "behavior_features": str(feature_path.relative_to(PROJECT_ROOT)),
        "source_frames": source_frames,
        "rendered_frames": rendered,
        "source_fps": source_fps,
        "output_fps": output_fps,
        "source_duration_sec": duration_sec,
        "output_duration_sec": output_duration,
        "duration_delta_sec": output_duration - duration_sec if finite(output_duration) else float("nan"),
        "source_resolution": [source_width, source_height],
        "output_resolution": [int(metadata.get("width", DISPLAY_WIDTH)), int(metadata.get("height", DISPLAY_HEIGHT))],
        "codec": codec,
        "output": str(output.relative_to(PROJECT_ROOT)),
        "artifact_sha256": {
            "source_video": sha256_file(source),
            "raw_tracking": sha256_file(raw_path),
            "cleaned_trajectory": sha256_file(clean_path),
            "behavior_features": sha256_file(feature_path),
            "rendered_video": sha256_file(output),
        },
        "screenshots": {name: str(path.relative_to(PROJECT_ROOT)) for name, path in screenshots.items()},
        "qa_checks": {
            "frame_count_matches_source": rendered == source_frames,
            "resolution_is_800x480": [int(metadata.get("width", 0)), int(metadata.get("height", 0))] == [800, 480],
            "h264_yuv420p": codec == "h264/yuv420p",
            "duration_within_0_2_sec": finite(output_duration) and abs(output_duration - duration_sec) <= 0.2,
        },
        "notes": [
            "Render chỉ dùng kết quả TOP đã có; không chạy detector/tracker/model.",
            "Track ID/trajectory_uid không phải biological identity.",
            "Tốc độ hiển thị là diag/s từ TOP feature windows.",
        ],
    }
    print(
        f"[PASS] {output} | {rendered} frames | source {source_fps:.6f} FPS | "
        f"output {output_fps:.6f} FPS | {codec}"
    )
    return report


def create_package(output_dir: Path, package_dir: Path) -> Path:
    package_dir.mkdir(parents=True, exist_ok=True)
    files = [
        PROJECT_ROOT / "pi_top" / "fish_monitor.py",
        PROJECT_ROOT / "pi_top" / "README_PI_TOP_PRECOMPUTED_DEMO.md",
        output_dir / "top_demo_1.mp4",
        output_dir / "top_demo_2.mp4",
    ]
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(f"Không thể đóng gói, thiếu: {path}")
        shutil.copy2(path, package_dir / path.name)
    archive = package_dir.parent / "pi_top_precomputed_demo.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for path in sorted(package_dir.iterdir()):
            tar.add(path, arcname=f"pi_top_precomputed_demo/{path.name}")
    print(f"[PASS] package: {archive}")
    return archive


def main() -> int:
    args = parse_args()
    cv2, np, pil = load_dependencies()
    output_dir = (PROJECT_ROOT / args.output_dir).resolve()
    qa_dir = (PROJECT_ROOT / args.qa_dir).resolve()
    video_ids = [args.video_id] if args.video_id else ["1", "2"]
    reports = [render_video(video_id, output_dir, qa_dir, cv2, np, pil) for video_id in video_ids]
    report_path = qa_dir / "qa_report.json"
    existing = {}
    if report_path.is_file():
        try:
            existing = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    all_reports = dict(existing) if isinstance(existing, dict) else {}
    for report in reports:
        all_reports[report["video_id"]] = report
    report_path.write_text(json.dumps(all_reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[PASS] QA report: {report_path}")
    if args.all and not args.no_package:
        create_package(output_dir, PROJECT_ROOT / "artifacts_local" / "pi_top_precomputed_demo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
