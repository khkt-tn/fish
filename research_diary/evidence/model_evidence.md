# Model evidence

## Front detector

Experiment `FRONT_DET_YOLOV8N_EVAL_001` đánh giá `best.pt` trên 254 ảnh valid với 995 đối tượng:

| Metric | Giá trị |
| --- | ---: |
| Precision | 0.967795 |
| Recall | 0.966466 |
| mAP50 | 0.989832 |
| mAP50-95 | 0.552514 |
| Parameters | 3.011.043 |
| GFLOPs | 8.191693 |

Model SHA-256: `750b0f8a1621f7214c8122467e5360ada69673ae4a8dc5bf3fd7b1e280287738`.

Nguồn: [`summary.json`](../../logs/detection/FRONT_DET_YOLOV8N_EVAL_001/summary.json), [`validation_metrics.csv`](../../results/detection/front_yolov8n_validation_metrics.csv).

## TOP detector

TOP detector có experiment riêng và không được coi là bản sao kết quả Front. Xem [`TOP_DET_YOLOV8N_EVAL_001/summary.json`](../../logs/detection/TOP_DET_YOLOV8N_EVAL_001/summary.json).

## Behavior model

Experiment `FRONT_BEHAVIOR_MODELS_001` có 98 cửa sổ được gán nhãn, 4 lớp, dùng grouped cross-validation. Random Forest là model tốt nhất trong bảng so sánh, nhưng macro-F1 trung bình chỉ khoảng 0.457 và lớp `FEEDING` có 7 cửa sổ, nên kết quả phải được trình bày thận trọng.

Nguồn: [`FRONT_BEHAVIOR_MODELS_001/summary.json`](../../logs/behavior/FRONT_BEHAVIOR_MODELS_001/summary.json), [`front_behavior_model_comparison.csv`](../../results/behavior/front_behavior_model_comparison.csv).
