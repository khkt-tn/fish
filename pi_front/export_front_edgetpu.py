#!/usr/bin/env python3
"""
Export the trained Front YOLO detector to Google Coral Edge TPU format.

RUN THIS ON x86_64 LINUX / WSL, NOT ON RASPBERRY PI.
The Edge TPU compiler is not available on ARM.

Default detector path matches the research pipeline:
    runs/front/yolov8n_front_v1_baseline/weights/best.pt

Recommended first demo export:
    imgsz=512

Use the same Front detection dataset YAML for INT8 calibration.
"""

from __future__ import annotations

import argparse
import platform
import shutil
from pathlib import Path

from ultralytics import YOLO


def find_project_root() -> Path:
    candidates = [
        Path("/home/diy-hus/fish"),
        Path.cwd(),
        Path.cwd().parent,
        Path.cwd().parent.parent,
    ]
    for p in candidates:
        if (p / "runs").exists() and (p / "results").exists():
            return p.resolve()
    return Path.cwd().resolve()


def find_data_yaml(project_root: Path) -> Path | None:
    candidates = [
        project_root / "datasets/front/detect_v1/data.yaml",
        project_root / "data/roboflow/front_detect_v1/data.yaml",
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    return None


def parser() -> argparse.ArgumentParser:
    root = find_project_root()

    p = argparse.ArgumentParser()
    p.add_argument(
        "--model",
        default=str(root / "runs/front/yolov8n_front_v1_baseline/weights/best.pt"),
    )
    p.add_argument(
        "--data",
        default=None,
        help="Front detection data.yaml used for INT8 calibration.",
    )
    p.add_argument("--imgsz", type=int, default=512)
    p.add_argument("--fraction", type=float, default=1.0)
    p.add_argument(
        "--copy-to",
        default=str(root / "deploy/pi_front/models"),
        help="Copy exported EdgeTPU model here while preserving its _edgetpu.tflite suffix.",
    )
    return p


def main() -> int:
    args = parser().parse_args()
    project_root = find_project_root()

    machine = platform.machine().lower()
    if machine in {"aarch64", "arm64", "armv7l", "armv6l"}:
        raise RuntimeError(
            "Edge TPU export must run on x86 Linux/WSL, not ARM/Raspberry Pi."
        )

    model_path = Path(args.model).expanduser().resolve()
    if not model_path.exists():
        raise FileNotFoundError(model_path)

    data_path = (
        Path(args.data).expanduser().resolve()
        if args.data
        else find_data_yaml(project_root)
    )
    if data_path is None or not data_path.exists():
        raise FileNotFoundError(
            "Front detection data.yaml not found. Pass it explicitly with --data."
        )

    print("Model:", model_path)
    print("Calibration data:", data_path)
    print("Image size:", args.imgsz)
    print("Fraction:", args.fraction)

    model = YOLO(str(model_path))

    exported = model.export(
        format="edgetpu",
        imgsz=int(args.imgsz),
        data=str(data_path),
        fraction=float(args.fraction),
        device="cpu",
    )

    exported_path = Path(str(exported)).expanduser().resolve()

    # Ultralytics normally returns the final file. Be defensive if a directory is returned.
    if exported_path.is_dir():
        matches = sorted(exported_path.rglob("*_edgetpu.tflite"))
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected exactly one *_edgetpu.tflite in {exported_path}, found {len(matches)}"
            )
        exported_path = matches[0]

    if not exported_path.exists():
        # Search around the source model as a final fallback.
        matches = sorted(model_path.parent.parent.parent.rglob("*_edgetpu.tflite"))
        if not matches:
            raise FileNotFoundError(
                f"Export reported {exported}, but no *_edgetpu.tflite was found."
            )
        exported_path = matches[-1]

    if not exported_path.name.endswith("_edgetpu.tflite"):
        raise RuntimeError(
            f"Unexpected EdgeTPU filename: {exported_path.name}. "
            "Keep the required '_edgetpu.tflite' suffix."
        )

    copy_dir = Path(args.copy_to).expanduser().resolve()
    copy_dir.mkdir(parents=True, exist_ok=True)
    copied = copy_dir / exported_path.name
    shutil.copy2(exported_path, copied)

    print("")
    print("EDGE TPU EXPORT COMPLETE")
    print("Exported:", exported_path)
    print("Copied:", copied)
    print("")
    print("Next: copy the .tflite file to Raspberry Pi without removing '_edgetpu.tflite'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
