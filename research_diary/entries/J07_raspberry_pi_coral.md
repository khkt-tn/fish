---
journal_id: J07
experiment_id: EXP-06
title: "Chuẩn bị pipeline trên Raspberry Pi và Coral Edge TPU"
date: "2026-08-19"
status: VERIFIED
authors:
  - "Phạm Duy Quang Anh"
  - "Nguyễn Quốc Minh"
tags:
  - raspberry-pi
  - coral
  - edge-deployment
evidence_level: medium
last_updated: "2026-08-29"
---

# Chuẩn bị pipeline trên Raspberry Pi và Coral Edge TPU

## 1. Mục tiêu

Đưa pipeline Front từ máy nghiên cứu sang thiết bị biên để kiểm tra khả năng detection, tracking, behavior và hiển thị gần thời gian thực.

## 2. Vấn đề cần giải quyết

Model PyTorch không chạy trực tiếp trên Coral; cần export INT8/Edge TPU đúng định dạng, giữ nhất quán tracker/feature và đo tốc độ trên phần cứng thật. Camera index và runtime Coral cũng phải được xác minh thay vì chỉ nhìn giao diện.

## 3. Thiết bị, dữ liệu và phần mềm

Repository có code hướng tới Raspberry Pi 4, Coral USB Edge TPU, OpenCV, Ultralytics, `tflite-runtime`, ByteTrack và Random Forest. File local `pi_front/models/best_full_integer_quant_edgetpu.tflite` tồn tại nhưng bị `.gitignore`.

## 4. Phương pháp thực hiện

Pipeline code là: frame Front → YOLO EdgeTPU → ByteTrack → làm sạch gap ngắn/median → feature 5 giây → Random Forest 4 lớp → giao diện và telemetry. Export được thiết kế chạy trên x86_64, không compile Edge TPU trên Raspberry Pi.

## 5. Quá trình thực hiện

Commit ngày 19/08/2026 thêm script export, ứng dụng demo, requirements và hướng dẫn chạy video trước rồi mới chuyển sang USB camera. Mô hình Edge TPU local cho thấy bước export có artifact, nhưng repository không lưu log export hoặc phiên chạy Pi.

## 6. Kết quả và quan sát

Code demo, tracker config, behavior schema và model artifact local đã sẵn sàng về mặt cấu trúc. Không có evidence xác nhận `Coral: ACTIVE`, latency, pipeline FPS, camera source hoặc output telemetry trên Raspberry Pi thật.

## 7. Vấn đề phát sinh

Mô tả về chọn sai camera index chưa có traceback/log. Vì vậy không ghi rằng lỗi đã xảy ra và đã sửa như một kết quả được xác minh. File model nặng cũng không thuộc phạm vi commit Git.

## 8. Điều chỉnh và cải tiến

Hướng dẫn hiện khuyến nghị kiểm tra trước bằng video cố định, giữ suffix `_edgetpu.tflite`, dùng cổng USB 3 và ghi Coral status, inference ms, pipeline FPS, CPU temperature/throttling.

## 9. Kết luận tại thời điểm thực hiện

Phần chuẩn bị triển khai được xác minh, nhưng chạy trên Raspberry Pi/Coral chỉ đạt `PARTIAL`. Chưa được gọi là benchmark hoặc triển khai thành công cho đến khi có log phần cứng.

## 10. Minh chứng

- [`README_PI_FRONT_DEMO.md`](../../pi_front/README_PI_FRONT_DEMO.md)
- [`export_front_edgetpu.py`](../../pi_front/export_front_edgetpu.py)
- [`fish_monitor.py`](../../pi_front/fish_monitor.py)
- Commit `622a94b808af2173b584cb6c5148603f93bac19c`
- `pi_front/models/best_full_integer_quant_edgetpu.tflite` (local, ignored, không stage)

## 11. Video minh họa

> 🎥 **V01 — Pipeline AI chạy trực tiếp trên Raspberry Pi + Coral**
<div class="video-container">
<iframe src="https://www.youtube.com/embed/SnY585wfMWQ" title="V02 — Video predicted camera FRONT" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

## 12. Đóng góp của thành viên

Quang Anh - Quốc Minh

