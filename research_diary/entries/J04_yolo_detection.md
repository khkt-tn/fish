---
journal_id: J04
experiment_id: EXP-04
title: "Huấn luyện và đánh giá mô hình phát hiện cá"
date: "2026-08-17"
status: VERIFIED
authors:
  - "Phạm Duy Quang Anh"
  - "Nguyễn Quốc Minh"
tags:
  - yolo
  - detection
  - validation
evidence_level: high
last_updated: "2026-08-29"
---

# Huấn luyện và đánh giá mô hình phát hiện cá

## 1. Mục tiêu

Huấn luyện detector nhỏ đủ tốt trên ảnh cá và có kích thước phù hợp với hướng triển khai thiết bị biên.

## 2. Vấn đề cần giải quyết

Detector cần cân bằng khả năng phát hiện với chi phí tính toán. Metric trên ảnh validation phải được tách khỏi count diagnostic trên video và không được dùng thay cho tracking identity.

## 3. Thiết bị, dữ liệu và phần mềm

Baseline Front dùng YOLOv8n, dataset Roboflow Front v1, ảnh 640, batch 16 và 100 epoch. Log môi trường ghi Conda `fish`; model tốt nhất ở epoch 74.

## 4. Phương pháp thực hiện

Model được train trên split train, sau đó reload `best.pt` và đánh giá riêng trên split valid. Nhóm lưu model SHA-256, metric bbox, parameters, GFLOPs và count diagnostic.

## 5. Quá trình thực hiện

Training tạo `FRONT_DET_YOLOV8N_001`; evaluation tạo `FRONT_DET_YOLOV8N_EVAL_001`. Kết quả reload gần với validation trong training, cho phép kiểm tra model artifact đã lưu đúng.

## 6. Kết quả và quan sát

Trên 254 ảnh valid với 995 đối tượng: Precision = 0,967795; Recall = 0,966466; mAP50 = 0,989832; mAP50-95 = 0,552514. Model có 3.011.043 parameters và khoảng 8,192 GFLOPs. Precision cao cho thấy phần lớn prediction giữ lại phù hợp ground truth; Recall cao cho thấy phần lớn cá trong valid được phát hiện.

## 7. Vấn đề phát sinh

Dataset có bbox và polygon rows lẫn nhau; Ultralytics bỏ segment và chỉ dùng boxes. Không có test split tùy chọn, nên toàn bộ số trên là validation metrics, không phải kết quả test độc lập.

## 8. Điều chỉnh và cải tiến

Nhóm dùng checksum model và so sánh metric sau reload. Failure audit trên video được tách riêng để không suy luận chất lượng theo thời gian chỉ từ validation ảnh tĩnh.

## 9. Kết luận tại thời điểm thực hiện

YOLOv8n Front đạt checkpoint detection validation với cảnh báo. Detector tốt là điều kiện cần, nhưng chưa tạo trajectory hoặc bảo đảm identity ổn định; bước sau phải đánh giá tracking.

## 10. Minh chứng

- [`FRONT_DET_YOLOV8N_EVAL_001/summary.json`](../../logs/detection/FRONT_DET_YOLOV8N_EVAL_001/summary.json)
- [`front_yolov8n_validation_metrics.csv`](../../results/detection/front_yolov8n_validation_metrics.csv)
- [`front_yolov8n_reproducibility_check.csv`](../../results/detection/front_yolov8n_reproducibility_check.csv)
- Commit `4cfac689c08d0f3f25bdee9cb8aac99d3202b9ee`

## 11. Video minh họa

### V01 — Video predicted camera TOP

<div class="video-container">
  <iframe
    src="https://youtu.be/WElMwtuTUAg"
    title="V01 — Video predicted camera TOP"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen>
  </iframe>
</div>

### V02 — Video predicted camera FRONT

<div class="video-container">
  <iframe
    src="https://youtu.be/qduDQEOlfUU"
    title="V02 — Video predicted camera FRONT"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen>
  </iframe>
</div>

## 12. Đóng góp của thành viên

Quang Anh - Quốc Minh

## 13. Công việc tiếp theo

Giữ nguyên detector và threshold theo experiment khi so sánh tracker; không chọn tracker chỉ dựa trên overlay.
