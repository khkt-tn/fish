# Chỉ mục minh chứng

## Git evidence

| Commit | Ngày UTC | Hoạt động | Bài |
| --- | --- | --- | --- |
| `b3b6d2fadcdd5e38f434cc2041eac51ba773943e` | 17/08/2026 | Audit dataset Front | J03 |
| `7e23b580488fe650fb3b379ca97f686d5b8ce9af` | 17/08/2026 | Train YOLOv8n Front | J04 |
| `4cfac689c08d0f3f25bdee9cb8aac99d3202b9ee` | 17/08/2026 | Evaluate YOLOv8n Front | J04 |
| `78ed4c11909367c4eef4724991449f74994d917f` | 17/08/2026 | ByteTrack ablation | J05 |
| `b0407b726d665e6f7798f35d9c9c6786242bd6fc` | 17/08/2026 | Tracker benchmark | J05 |
| `622a94b808af2173b584cb6c5148603f93bac19c` | 19/08/2026 | Front behavior artifacts và Coral demo code | J06–J07 |
| `4c582fc012f8e37bf7dd003e034aa7ee1676bed3` | 29/08/2026 | TOP detection/tracking | J02, J04–J06 |
| `cc74ce9c4e7873380a0f88d360817f29b472bcd6` | 29/08/2026 | TOP behavior features | J06, J08 |
| `dbc51a9fec769a9f1754d5ba479f5b77317b39fd` | 29/08/2026 | Environment–behavior analysis | J08–J09 |

## Model evidence

| Model | Config/log | Result | Bài |
| --- | --- | --- | --- |
| Front YOLOv8n | [`FRONT_DET_YOLOV8N_EVAL_001`](../logs/detection/FRONT_DET_YOLOV8N_EVAL_001/summary.json) | [`front_yolov8n_validation_metrics.csv`](../results/detection/front_yolov8n_validation_metrics.csv) | J04 |
| Front Random Forest | [`FRONT_BEHAVIOR_MODELS_001`](../logs/behavior/FRONT_BEHAVIOR_MODELS_001/summary.json) | [`front_behavior_model_comparison.csv`](../results/behavior/front_behavior_model_comparison.csv) | J06 |
| TOP YOLOv8n | [`TOP_DET_YOLOV8N_EVAL_001`](../logs/detection/TOP_DET_YOLOV8N_EVAL_001/summary.json) | [`top_yolov8n_validation_metrics.csv`](../results/detection/top_yolov8n_validation_metrics.csv) | J04 |

## Dataset evidence

| Dataset/version | Metadata | Audit | Bài |
| --- | --- | --- | --- |
| Front Roboflow v1 | [`roboflow_versions.csv`](../logs/data/roboflow_versions.csv) | [`front_dataset_manifest.json`](../results/detection/front_dataset_manifest.json) | J03 |
| TOP Roboflow v2 | [`roboflow_versions.csv`](../logs/data/roboflow_versions.csv) | [`top_dataset_manifest.json`](../results/detection/top_dataset_manifest.json) | J03 |

## Tracking evidence

| Nội dung | Evidence | Bài |
| --- | --- | --- |
| ByteTrack B15/B30/B60 | [`front_bytetrack_ablation.csv`](../results/tracking/front_bytetrack_ablation.csv) | J05 |
| ByteTrack và BoT-SORT | [`front_tracker_benchmark.csv`](../results/tracking/front_tracker_benchmark.csv) | J05 |
| TOP ByteTrack B15 | [`top_bytetrack_baseline_summary.csv`](../results/tracking/top_bytetrack_baseline_summary.csv) | J05–J06 |
| MOT theo segment | [`front_mot_official_metrics_by_segment.csv`](../results/tracking/front_mot_official_metrics_by_segment.csv) | J05 |

## Environment evidence

| Artifact | Vai trò | Bài |
| --- | --- | --- |
| [`16_environment_behavior_analysis.ipynb`](../notebooks/16_environment_behavior_analysis.ipynb) | Notebook phân tích | J08–J09 |
| [`TOP_ENV_BEHAVIOR_001/summary.json`](../logs/environment/TOP_ENV_BEHAVIOR_001/summary.json) | Provenance, giới hạn, quyết định | J08–J09 |
| [`environment_session_summary.csv`](../results/environment/environment_session_summary.csv) | Hai phiên và sensor đầu/cuối | J08–J09 |
| [`environment_behavior_summary.csv`](../results/environment/environment_behavior_summary.csv) | Tóm tắt cá thể và nhóm | J09 |
| [`environment_behavior_comparison.csv`](../results/environment/environment_behavior_comparison.csv) | Sáu so sánh mô tả | J09 |

Chi tiết hơn được tách trong thư mục [`evidence/`](evidence/).
