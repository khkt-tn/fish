# Báo cáo phiên xây dựng nhật ký

## Phạm vi

Ngày mốc nội dung: `2026-08-29`

Múi giờ nhật ký: `Asia/Bangkok (+07:00)`

Phiên này chỉ audit tĩnh và tạo Markdown trong `research_diary/`. Không chạy notebook, training, inference, benchmark, login, upload hay push.

## Files created

Tổng cộng: **31 file Markdown**.

- 7 file cấp root: `README`, giới thiệu, timeline, media, evidence, contribution và báo cáo phiên.
- 16 bài trong `entries/` từ J01 đến J16.
- 2 template trong `templates/`.
- 6 file chi tiết trong `evidence/`.

## Evidence found

- Git history/checkpoint từ 17/08 đến 29/08/2026.
- Front Roboflow v1 và TOP Roboflow v2 cùng manifest/audit.
- Front YOLOv8n train/evaluation với model hash và đầy đủ Precision, Recall, mAP50, mAP50-95.
- ByteTrack ablation, tracker benchmark, MOT tables và TOP tracking diagnostic.
- Front/TOP behavior feature summaries và schema.
- Code demo Raspberry Pi/Coral cùng Edge TPU model local bị ignore.
- Hai sensor JSON, hai bảng environment–behavior local, ba result CSV, sáu plot và log `TOP_ENV_BEHAVIOR_001`.
- Commit Checkpoint 16: `dbc51a9fec769a9f1754d5ba479f5b77317b39fd`.

## Entry status

### VERIFIED

- J02 — TOP/FRONT data collection
- J03 — Roboflow dataset
- J04 — YOLO detection
- J05 — fish tracking
- J06 — behavior features
- J09 — session-level sensor/behavior integration
- J10 — descriptive environment/behavior analysis

### PARTIAL

- J01 — acquisition/collector/rclone history lacks direct artifacts
- J07 — Pi/Coral code and local model exist; runtime evidence is absent
- J08 — optimization direction exists; before/after benchmark is absent

### PLANNED

- J11–J16

## Unresolved items

- Mốc 30/07, 31/07, 02/08 và 10/08/2026 chưa có evidence trong history hiện tại.
- Không tìm thấy `collector.log`, `Fish_Front_AI_dataset` hoặc log rclone.
- Chưa xác minh ngày raw Front, ý nghĩa T1/T2 hoặc contribution cá nhân.
- Không có Pi/Coral runtime log, camera-index incident log hoặc evidence 3 FPS.
- HOTA trong summary MOT là `null`; ba segment official bị skip do identity uncertain.
- Notebook 18 và 19 chưa tồn tại tại ngày mốc.

## Media required

V01–V12 đều ở trạng thái `TODO_UPLOAD` và dùng `TODO_YOUTUBE_URL`/`TODO_YOUTUBE_VIDEO_ID`. Cần bổ sung ảnh setup Raspberry Pi/camera, màn hình Roboflow, live Coral và benchmark trước/sau. Raw/overlay video chỉ được dùng làm nguồn local, không commit.

## Metrics still missing

- Raspberry Pi/Coral: pipeline FPS, inference latency, CPU/RAM, temperature/throttling và benchmark 320/512.
- MOT: HOTA và official metric cho các segment identity uncertain nếu protocol sau này cho phép.
- Statistical validation: independent replicate count, effect size/CI/sensitivity analysis nếu thiết kế đủ dữ liệu.

Metric detector Front không còn để trống: Precision `0.967795`, Recall `0.966466`, mAP50 `0.989832`, mAP50-95 `0.552514`, 3.011.043 parameters và 8,191693 GFLOPs đều lấy từ log gốc.

## Contribution fields

Mọi phân công cá nhân được giữ là `TO_VERIFY_WITH_STUDENTS`. Git author không được dùng để suy ra đóng góp khoa học.

## Repository safety

- Worktree có thay đổi ngoài phạm vi tồn tại trước phiên; chúng không được chỉnh sửa hoặc stage.
- Chỉ `research_diary/` được phép stage cho commit yêu cầu.
- Raw data, outputs, runs, models và file Edge TPU không bị sửa hoặc stage.
- Commit của phiên không thể tự chứa SHA của chính nó; SHA chính xác được báo ở câu trả lời cuối và có thể xem bằng `git log -1`.
