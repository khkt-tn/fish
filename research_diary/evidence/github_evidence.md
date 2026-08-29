# Git evidence

## Phạm vi lịch sử hiện có

Branch hiện tại là `main`, theo dõi `origin/main`. Commit đầu tiên trong lịch sử local hiện có là `4f9648a` ngày 17/08/2026; vì vậy Git không xác minh được các mốc 30/07, 31/07, 02/08 hoặc 10/08 được nêu như mốc tham khảo.

## Chuỗi checkpoint chính

| SHA | Ngày UTC | Subject | Evidence khoa học |
| --- | --- | --- | --- |
| `4f9648a905e00828703cd2d329e82f0408134b67` | 17/08/2026 | `checkpoint-00-environment` | Môi trường máy nghiên cứu |
| `b3b6d2fadcdd5e38f434cc2041eac51ba773943e` | 17/08/2026 | `checkpoint-02-front-dataset-audit` | Dataset Front |
| `7e23b580488fe650fb3b379ca97f686d5b8ce9af` | 17/08/2026 | `checkpoint-03-front-yolov8n-baseline` | Training baseline |
| `4cfac689c08d0f3f25bdee9cb8aac99d3202b9ee` | 17/08/2026 | `checkpoint-04-front-yolov8n-evaluation` | Validation detector |
| `78ed4c11909367c4eef4724991449f74994d917f` | 17/08/2026 | `checkpoint-07-front-bytetrack-ablation` | ByteTrack buffer ablation |
| `b0407b726d665e6f7798f35d9c9c6786242bd6fc` | 17/08/2026 | `checkpoint-08-front-tracker-benchmark` | Tracker benchmark |
| `622a94b808af2173b584cb6c5148603f93bac19c` | 19/08/2026 | `checkpoint-13-front-behavior-and-coral-demo` | Front behavior và code demo Coral |
| `4c582fc012f8e37bf7dd003e034aa7ee1676bed3` | 29/08/2026 | `checkpoint-14-top-detection-tracking` | TOP detection/tracking |
| `cc74ce9c4e7873380a0f88d360817f29b472bcd6` | 29/08/2026 | `checkpoint-15-top-behavior-features` | TOP features |
| `dbc51a9fec769a9f1754d5ba479f5b77317b39fd` | 29/08/2026 | `checkpoint-16-environment-behavior-analysis` | Environment–behavior analysis |

`checkpoint-16-environment-behavior-analysis` là commit subject, không phải Git tag trong repository local tại thời điểm audit.
