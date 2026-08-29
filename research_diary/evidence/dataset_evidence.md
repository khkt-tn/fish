# Dataset evidence

## Front Roboflow version 1

- Workspace: `phys-hus`
- Project: `fish_front_detection`
- Version: `1`
- Export format: `yolov8`
- Export metadata local: 14/08/2026
- Tổng: 1.269 ảnh, 4.883 annotation rows/boxes được audit
- Split: train 1.015 ảnh/3.888 boxes; valid 254 ảnh/995 boxes; không có test split trong evaluation chính
- Cảnh báo: có 41 polygon rows ở train và 10 ở valid; pipeline detection chỉ dùng boxes.

Minh chứng:

- [`front_dataset_manifest.json`](../../results/detection/front_dataset_manifest.json)
- [`front_dataset_audit_summary.csv`](../../results/detection/front_dataset_audit_summary.csv)
- [`front_class_distribution.csv`](../../results/detection/front_class_distribution.csv)

## TOP Roboflow version 2

- Workspace: `phys-hus`
- Project: `fish-top-detection`
- Version: `2`
- Export format: `yolov8`
- Export metadata local: 29/08/2026
- Tổng metadata local: 1.509 ảnh.
- Metadata export không đủ để suy ra phân bố T1/T2.

Minh chứng:

- [`top_dataset_manifest.json`](../../results/detection/top_dataset_manifest.json)
- [`top_dataset_audit_summary.csv`](../../results/detection/top_dataset_audit_summary.csv)
- [`roboflow_versions.csv`](../../logs/data/roboflow_versions.csv)

## Chưa xác minh

- Ngày và người thực hiện từng phần gán nhãn.
- Quy tắc tách theo video nguồn để chứng minh không leakage giữa train/valid.
- Ý nghĩa sinh học của T1/T2; không được tự suy diễn từ tên.
