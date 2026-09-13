#!/usr/bin/env python3
"""Lightweight fullscreen player for the precomputed CAMERA TOP demo."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phát video CAMERA TOP đã xử lý trước bằng mpv. "
            "Raspberry Pi không chạy suy luận AI."
        )
    )
    parser.add_argument(
        "--video",
        default="1",
        help="1, 2, hoặc đường dẫn MP4 (mặc định: 1)",
    )
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Mở cửa sổ thay vì fullscreen (hữu ích khi kiểm tra)",
    )
    return parser.parse_args()


def resolve_video(value: str) -> Path:
    if value in {"1", "2"}:
        candidates = [SCRIPT_DIR / "demo" / f"top_demo_{value}.mp4"]
    else:
        supplied = Path(value).expanduser()
        candidates = [supplied] if supplied.is_absolute() else [Path.cwd() / supplied, SCRIPT_DIR / supplied]

    checked: list[Path] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in checked:
            continue
        checked.append(resolved)
        if resolved.is_file():
            return resolved

    locations = ", ".join(str(path) for path in checked)
    raise FileNotFoundError(f"Không tìm thấy video demo. Đã kiểm tra: {locations}")


def main() -> int:
    args = parse_args()
    try:
        video_path = resolve_video(args.video)
    except FileNotFoundError as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2

    mpv = shutil.which("mpv")
    if mpv is None:
        print("LỖI: chưa cài mpv. Chạy: sudo apt update && sudo apt install -y mpv", file=sys.stderr)
        return 2

    command = [mpv, "--loop-file=inf", "--keep-open=no", "--osd-level=1"]
    if not args.windowed:
        command.append("--fullscreen")
    command.append(str(video_path))

    print(f"Đang phát video đã xử lý trước: {video_path}")
    print("Phím mpv: SPACE tạm dừng/tiếp tục, f fullscreen, ←/→ tua, q thoát")
    try:
        return subprocess.run(command, check=False).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
