# CODEX SPEC — TOP CAMERA PIPELINE
## Project: Nghiên cứu hành vi của cá bằng AI
## Repository: https://github.com/khkt-tn/fish
## Roboflow TOP: https://app.roboflow.com/phys-hus/fish-top-detection/browse?queryText=&pageSize=50&startingIndex=0&browseQuery=true

> Version của tài liệu này đã được cập nhật dựa trên repository FRONT thực tế trên GitHub và thông tin môi trường hiện tại.
>
> Mục tiêu hiện tại: **bắt đầu phần TOP đúng theo workflow của project, không thiết kế lại project, không phá pipeline FRONT đã hoàn thiện.**

---

# 0. NGUYÊN TẮC CAO NHẤT

Codex phải đọc và tuân thủ trước tiên:

```text
AGENTS.md
FISH_AI_PROJECT_WORKFLOW.md
```

Nếu file này xung đột với hai file trên thì:

1. ưu tiên `AGENTS.md`;
2. sau đó ưu tiên `FISH_AI_PROJECT_WORKFLOW.md`;
3. chỉ khác đi nếu người dùng có chỉ đạo rõ ràng mới hơn.

Pipeline FRONT đã hoàn thành là **reference implementation thực tế** cho TOP.

Không được:

- thiết kế lại toàn bộ pipeline;
- tự động chạy hàng loạt notebook;
- tự động push GitHub;
- ghi đè kết quả FRONT;
- đổi dataset version tùy ý;
- tự tạo môi trường Conda mới;
- tự nhập/lưu API key;
- tự thực hiện OAuth/login;
- commit dataset/model/video lớn.

---

# 1. TRẠNG THÁI PROJECT ĐÃ XÁC MINH

## 1.1. GitHub

Repository:

```text
https://github.com/khkt-tn/fish
```

Default branch:

```text
main
```

Reference HEAD tại thời điểm tạo spec:

```text
622a94b808af2173b584cb6c5148603f93bac19c
checkpoint-13-front-behavior-and-coral-demo
```

Các checkpoint FRONT quan trọng hiện đã có:

```text
checkpoint-00-environment
checkpoint-02-front-dataset-audit
checkpoint-03-front-yolov8n-baseline
checkpoint-04-front-yolov8n-evaluation
checkpoint-06a-front-visibility-audit
checkpoint-07-front-bytetrack-ablation
checkpoint-07a-video4-trajectory-overlay
checkpoint-08-front-tracker-benchmark
checkpoint-13-front-behavior-and-coral-demo
```

Codex KHÔNG được hard reset local về commit trên.

Phải kiểm tra local trước:

```bash
git status --short
git branch --show-current
git remote -v
git rev-parse HEAD
git log --oneline --decorate -n 20
```

Nếu local có commit mới hơn hoặc thay đổi chưa commit:

- không xóa;
- không reset;
- báo cáo;
- tiếp tục theo trạng thái local hợp lệ.

Nếu working tree sạch và cần đồng bộ:

```bash
git fetch origin
git status
git log --oneline --decorate --graph --all -n 20
```

Chỉ `git pull --ff-only` nếu chắc chắn an toàn.

---

# 2. WORKFLOW HIỆN TẠI: TOP BẮT ĐẦU Ở NOTEBOOK 14

Workflow chuẩn của repo quy định:

```text
00 → 01 → 02 → ... → 13 → 14 → 15 → 16 → ... → 19
```

FRONT hiện đã hoàn thành đến Notebook 13.

Notebook TOP tiếp theo phải là:

```text
notebooks/14_top_detection_tracking.ipynb
```

Sau đó mới đến:

```text
notebooks/15_top_behavior_features.ipynb
```

Hiện repository chưa có:

```text
notebooks/14_top_detection_tracking.ipynb
```

Do đó task hiện tại là:

> **Chuẩn bị Notebook 14 — TOP detection + tracking theo pipeline FRONT đã có.**

Không tự nhảy sang Notebook 15.

Không làm sensor sync.

Không làm final Raspberry Pi benchmark.

Không làm final results.

---

# 3. QUY TẮC THỰC THI NOTEBOOK CỰC KỲ QUAN TRỌNG

Theo `AGENTS.md`:

Từ Notebook 01 trở đi:

> Codex chuẩn bị notebook, nhưng USER là người trực tiếp bấm **Run** hoặc **Run All** trong VS Code.

Vì vậy Codex phải làm đúng trình tự:

```text
1. Audit repo
2. Audit input
3. Chuẩn bị Notebook 14
4. Kiểm tra notebook về mặt cấu trúc/code tĩnh
5. Báo cho user file đã sẵn sàng
6. STOP
7. User tự Run/Run All
8. Sau khi user báo đã chạy xong, Codex mới đọc/kiểm tra output
9. Hoàn thiện log/results
10. Báo cáo
11. STOP chờ duyệt trước Notebook 15
```

Codex KHÔNG được tự động dùng:

```bash
jupyter nbconvert --execute ...
papermill ...
python chạy lại toàn bộ notebook ...
```

để thay user thực thi Notebook 14.

Có thể dùng các kiểm tra tĩnh như:

```bash
python -m py_compile ...
```

cho file `.py` hỗ trợ nếu có.

---

# 4. MÔI TRƯỜNG CONDA ĐÃ CÓ

Hai môi trường hiện có:

```text
fish
/home/diy-hus/miniconda3/envs/fish
```

và:

```text
fish-export
/home/diy-hus/miniconda3/envs/fish-export
```

## 4.1. Vai trò `fish`

`fish` là môi trường nghiên cứu chính.

Dùng cho:

```text
Notebook 14
dataset audit
YOLO training
YOLO validation
video inference
tracking
trajectory generation
metrics
plots
research logging
```

Repository hiện ghi:

```text
Python 3.11
ultralytics 8.4.120
```

và environment chính được quản lý tại:

```text
environment/environment.yml
environment/pip_freeze.txt
```

Trước Notebook 14 phải kiểm tra:

```bash
conda activate fish
which python
python --version
python -c "import sys; print(sys.executable)"
python -c "import ultralytics; print(ultralytics.__version__)"
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

Nếu GPU có:

```bash
python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

Không broad-upgrade package.

Không chạy:

```bash
pip install -U ultralytics
pip install -U torch
conda update --all
```

trừ khi người dùng phê duyệt riêng.

---

## 4.2. Vai trò `fish-export`

`fish-export` là môi trường chuyên dụng cho export/deployment.

KHÔNG dùng `fish-export` để:

```text
train TOP baseline
evaluate TOP baseline
tracking research
Notebook 14
Notebook 15
```

Dùng môi trường này sau này cho các bước như:

```text
TFLite
INT8
EdgeTPU
Coral export
deployment compatibility
```

### Quan trọng

Notebook 14 chưa phải Notebook 18.

Do đó:

> **Không export EdgeTPU trong task Notebook 14 trừ khi user yêu cầu riêng.**

Việc đã có `fish-export` chỉ cần được ghi nhận trong spec để dùng đúng giai đoạn sau.

Không ghi đè:

```text
environment/environment.yml
environment/pip_freeze.txt
```

bằng package list của `fish-export`.

Khi đến bước export, environment của `fish-export` phải được log riêng trong:

```text
logs/deployment/<experiment_id>/environment.txt
```

---

# 5. ROBOFLOW TOP — SOURCE OF TRUTH ĐÃ CHỐT

Roboflow workspace:

```text
phys-hus
```

Project:

```text
fish-top-detection
```

Project URL:

```text
https://app.roboflow.com/phys-hus/fish-top-detection/browse?queryText=&pageSize=50&startingIndex=0&browseQuery=true
```

Version theo repository hiện tại:

```text
2
```

Format:

```text
yolov8
```

Local root theo `configs/data_sources.yaml`:

```text
data/roboflow/top_detect_v2
```

Config repo đã khai báo:

```yaml
top:
  source: roboflow
  workspace: phys-hus
  project: fish-top-detection
  version: 2
  format: yolov8
  local_root: data/roboflow/top_detect_v2
```

### Đây là version chuẩn cho Notebook 14

Không tự chọn:

```text
version 1
latest version
version mới nhất trong UI
```

nếu chưa có chỉ đạo mới từ user.

Ngay cả khi Roboflow UI hiện có version > 2:

> Notebook 14 baseline vẫn phải dùng **version 2** để đúng provenance hiện tại, trừ khi user yêu cầu cập nhật `configs/data_sources.yaml`.

---

# 6. AUTHENTICATION / ROBOFLOW LOGIN

User đã xác nhận có tài khoản.

Tuy nhiên theo policy của repo:

- login;
- OAuth;
- API key;
- token;
- credential setup;

phải do USER thao tác thủ công.

Codex không được:

```text
xin user paste API key vào notebook
in API key ra terminal
ghi API key vào .env trong repo
commit API key
chèn token vào URL
tự tạo credential
```

## 6.1. Trước tiên kiểm tra dataset đã có local chưa

```bash
ls -la data/roboflow
ls -la data/roboflow/top_detect_v2
test -f data/roboflow/top_detect_v2/data.yaml && echo "TOP DATASET FOUND"
```

Nếu dataset đã có:

> Không cần Roboflow login nữa. Tiếp tục audit local dataset.

---

## 6.2. Nếu TOP dataset chưa có local

Codex phải dừng ở authentication/download gate và hướng dẫn user tải đúng:

```text
Workspace: phys-hus
Project: fish-top-detection
Version: 2
Format: YOLOv8
```

Đích cuối phải là:

```text
data/roboflow/top_detect_v2/data.yaml
```

và các thư mục tương ứng.

Ví dụ:

```text
data/roboflow/top_detect_v2/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── ...
```

Có thể có `test/` hoặc không tùy version thật.

Không giả định.

---

## 6.3. Không bắt buộc cài package `roboflow`

Môi trường `fish` hiện không cần bị thay đổi chỉ để download dữ liệu.

Ưu tiên:

```text
user download/export trực tiếp đúng Version 2 từ Roboflow UI
→ giải nén vào data/roboflow/top_detect_v2
```

Nếu user muốn sử dụng Roboflow SDK/API thì xử lý thành bước riêng.

Không tự `pip install roboflow` trong Notebook 14 chỉ vì package chưa có.

---

# 7. CẬP NHẬT METADATA ROBOFLOW SAU KHI DATASET CÓ LOCAL

File hiện có:

```text
logs/data/roboflow_versions.csv
```

Hiện FRONT đã có row:

```csv
front,phys-hus,fish_front_detection,1,yolov8,data/roboflow/front_detect_v1,...
```

Sau khi TOP version 2 được xác nhận local, thêm row TOP:

```csv
top,phys-hus,fish-top-detection,2,yolov8,data/roboflow/top_detect_v2,<download_datetime>
```

Không thêm API key.

Không commit dataset.

Chỉ metadata nhỏ được commit.

---

# 8. FRONT REFERENCE — DATASET

FRONT hiện dùng:

```text
data/roboflow/front_detect_v1
```

Roboflow:

```text
workspace: phys-hus
project: fish_front_detection
version: 1
format: yolov8
```

FRONT dataset audit đã ghi:

```text
train images: 1015
valid images: 254
train boxes: 3888
valid boxes: 995
```

Class hiện tại:

```text
class_id: 0
class_name: Ca
```

FRONT không có test split trong evaluation chính thức.

### Warning FRONT quan trọng

FRONT từng có cả YOLO bbox rows và polygon rows:

```text
train polygon rows: 41
valid polygon rows: 10
```

Ultralytics đã cảnh báo mixed detect/segment annotations và chỉ dùng box.

Vì vậy TOP audit bắt buộc kiểm tra điều này.

Không được mặc định rằng TOP labels sạch chỉ vì export từ Roboflow.

---

# 9. FRONT REFERENCE — YOLO BASELINE

Experiment:

```text
FRONT_DET_YOLOV8N_001
```

Config chính thức:

```yaml
model: yolov8n.pt
data: data/roboflow/front_detect_v1/data.yaml
imgsz: 640
epochs: 100
batch: 16
device: 0
seed: 42
workers: 4
optimizer: auto
project: runs/front
name: yolov8n_front_v1_baseline
```

TOP baseline phải bắt đầu từ đúng điều kiện đối chứng này.

Không tuning trước baseline.

---

# 10. FRONT REFERENCE — KẾT QUẢ YOLO

Best epoch:

```text
74
```

Reloaded best-model validation:

```text
Precision   = 0.9677949493
Recall      = 0.9664655248
mAP50       = 0.9898324652
mAP50-95    = 0.5525137653
```

Validation:

```text
254 images
995 objects
```

Model:

```text
parameters ≈ 3,011,043
GFLOPs ≈ 8.1917
model size ≈ 5.95 MB
```

Inference validation hardware:

```text
~4.00 ms/image
~249.7 FPS
```

### Không hiểu sai FPS

Đây là FPS ở hardware evaluation của research machine.

Không được gọi đây là:

```text
Raspberry Pi FPS
Coral FPS
real-world pipeline FPS
```

---

# 11. FRONT REFERENCE — TRACKER ĐANG ĐƯỢC DÙNG CHO DEMO

File:

```text
configs/trackers/front_bytetrack_b15.yaml
```

Nội dung:

```yaml
tracker_type: bytetrack
track_high_thresh: 0.68
track_low_thresh: 0.50
new_track_thresh: 0.68
track_buffer: 15
match_thresh: 0.80
fuse_score: true
```

Đây là config FRONT đang được đóng gói cho Raspberry Pi demo.

Đối với TOP:

- không dùng chung file bằng cách sửa trực tiếp;
- có thể dùng các giá trị này làm **transfer baseline**;
- nhưng phải đánh giá độc lập trên video TOP.

Tạo file riêng nếu Notebook 14 cần:

```text
configs/trackers/top_bytetrack_b15.yaml
```

Ban đầu nội dung copy 1:1 từ FRONT.

Không tuning ngay.

---

# 12. TOP KHÔNG ĐƯỢC COI LÀ FRONT COPY ĐƠN GIẢN

Workflow khoa học xác định TOP ưu tiên:

```text
x-y trajectory
speed
distance
turning
wall-following
center/perimeter
nearest-neighbor distance
pairwise distance
group centroid
group area
alignment
aggregation / dispersion
```

FRONT ưu tiên các đặc trưng theo trục đứng.

Do đó:

```text
Detection architecture có thể đối xứng FRONT
Tracking methodology có thể đối xứng FRONT
Behavior features KHÔNG được copy nguyên FRONT
```

Notebook 14 chỉ làm:

```text
TOP detection
TOP tracking
TOP trajectory evidence cơ bản
```

Notebook 15 mới làm:

```text
TOP behavior features
```

---

# 13. KHÔNG GHÉP ID FRONT VÀ TOP

Tuyệt đối không giả định:

```text
Front ID 3 == Top ID 3
```

Track ID chỉ là tracker identity trong từng camera.

Hai camera trước hết chỉ liên hệ qua:

```text
timestamp
experimental condition
tank
video session
```

Cross-camera identity không thuộc Notebook 14.

---

# 14. GIAI ĐOẠN A — AUDIT REPO TRƯỚC KHI TẠO NOTEBOOK 14

Codex chạy read-only inspection:

```bash
git status --short
git branch --show-current
git remote -v
git rev-parse HEAD
git log --oneline --decorate -n 30
```

Kiểm tra:

```bash
ls -la
ls -la notebooks
ls -la configs
ls -la configs/trackers
ls -la logs/detection
ls -la logs/tracking
ls -la results/detection
ls -la results/tracking
```

Đọc:

```text
AGENTS.md
FISH_AI_PROJECT_WORKFLOW.md
configs/data_sources.yaml
configs/paths.yaml
.gitignore
```

Đọc reference notebook:

```text
notebooks/02_dataset_detection_audit.ipynb
notebooks/03_yolo_detection_training.ipynb
notebooks/04_yolo_detection_evaluation.ipynb
notebooks/05_front_video_detection.ipynb
notebooks/06_front_detection_failure_audit.ipynb
notebooks/07_front_bytetrack_ablation.ipynb
notebooks/08_front_tracker_benchmark.ipynb
```

Không cần copy nguyên toàn bộ notebook.

Phải trích đúng logic tái sử dụng.

---

# 15. GIAI ĐOẠN B — AUDIT TOP DATASET V2

Dataset:

```text
data/roboflow/top_detect_v2
```

## 15.1. Kiểm tra cấu trúc thật

Không giả định `valid` hay `val`.

Đọc:

```bash
find data/roboflow/top_detect_v2 -maxdepth 3 -type d | sort
cat data/roboflow/top_detect_v2/data.yaml
```

Ghi lại:

```text
train path
valid/val path
test path nếu có
names
nc nếu có
```

---

## 15.2. Class mapping

Đối chiếu TOP với FRONT.

FRONT hiện:

```text
0: Ca
```

Nếu TOP dùng cùng đối tượng cá:

> class ID/name phải tương thích.

Nếu TOP Roboflow version 2 có tên class khác về chữ hoa/thường hoặc ngôn ngữ:

- không tự đổi trước khi báo cáo;
- ghi rõ khác biệt;
- chỉ normalize nếu thật sự cần và phải log.

---

## 15.3. Audit bắt buộc

Kiểm tra từng split:

```text
n_images
n_label_files
missing labels
orphan labels
empty labels
total boxes
bbox rows
polygon rows
mixed-format files
invalid class IDs
invalid normalized coordinates
corrupt images
image resolutions
```

YOLO bbox hợp lệ:

```text
class_id x_center y_center width height
```

với:

```text
0 <= x_center <= 1
0 <= y_center <= 1
0 < width <= 1
0 < height <= 1
```

---

## 15.4. Duplicate / leakage

Nếu ảnh được trích từ video:

Kiểm tra:

```text
exact duplicate hash
file stem patterns
video/session naming
T1/T2 distribution
nearby frames crossing train/valid/test
```

Không tự split lại dataset.

Chỉ báo cáo risk.

---

## 15.5. T1 / T2

Nếu filename hoặc metadata cho phép:

Thống kê theo:

```text
T1
T2
```

Tối thiểu:

```text
images/split/tank
boxes/split/tank
```

Nếu không suy ra được tank:

ghi:

```text
tank stratification unavailable from exported metadata
```

Không đoán.

---

# 16. TOP DATASET EVIDENCE PHẢI SINH

Tạo các evidence nhỏ tương tự FRONT:

```text
results/detection/top_dataset_audit_summary.csv
results/detection/top_class_distribution.csv
results/detection/top_dataset_manifest.json
```

Nếu phù hợp:

```text
results/detection/top_annotation_format_summary.csv
results/detection/top_boundary_warnings.csv
```

Log:

```text
logs/detection/TOP_DATASET_AUDIT_V2_001/
├── config.yaml
├── environment.txt
└── summary.json
```

Không commit raw dataset.

---

# 17. GIAI ĐOẠN C — TẠO NOTEBOOK 14

Tạo:

```text
notebooks/14_top_detection_tracking.ipynb
```

Notebook phải có các section rõ ràng.

---

## 17.1. Section 1 — Title / scientific objective

Ví dụ:

```text
Notebook 14 — TOP Detection and Tracking
```

Mục tiêu:

```text
1. validate TOP Roboflow version 2;
2. train TOP YOLOv8n baseline under matched FRONT conditions;
3. evaluate detector;
4. run detector on TOP video;
5. establish a TOP ByteTrack baseline;
6. produce reproducible evidence for Notebook 15.
```

Không claim behavior classification trong Notebook 14.

---

## 17.2. Section 2 — CONFIG

Notebook phải tập trung toàn bộ config ở đầu.

Ví dụ logic:

```python
CAMERA = "top"

DATASET_VERSION = 2
ROBOFLOW_WORKSPACE = "phys-hus"
ROBOFLOW_PROJECT = "fish-top-detection"

MODEL_NAME = "yolov8n.pt"
IMGSZ = 640
EPOCHS = 100
BATCH = 16
DEVICE = 0
SEED = 42
WORKERS = 4
OPTIMIZER = "auto"

TRAIN_EXPERIMENT_ID = "TOP_DET_YOLOV8N_001"
```

Không hard-code:

```python
PROJECT_ROOT = Path("/home/diy-hus/fish")
```

Dùng repo-relative project-root resolution.

---

# 18. TOP YOLO BASELINE — GIỮ ĐIỀU KIỆN FRONT

Baseline TOP:

```yaml
model: yolov8n.pt
data: data/roboflow/top_detect_v2/data.yaml
imgsz: 640
epochs: 100
batch: 16
device: 0
seed: 42
workers: 4
optimizer: auto
project: runs/top
name: yolov8n_top_v2_baseline
```

Experiment ID:

```text
TOP_DET_YOLOV8N_001
```

### Không đổi ở baseline

Không thay:

```text
YOLOv8n → YOLO11n
640 → 320
batch 16 → khác
epochs 100 → khác
optimizer auto → khác
seed 42 → khác
augmentation tuning
```

nếu không có lỗi bắt buộc.

Mục đích:

> so sánh camera TOP và FRONT dưới điều kiện detector tương đồng.

---

# 19. TOP TRAIN OUTPUT

Ultralytics local heavy output:

```text
runs/top/yolov8n_top_v2_baseline/
```

Không commit folder này.

Evidence Git:

```text
logs/detection/TOP_DET_YOLOV8N_001/
├── config.yaml
├── environment.txt
└── summary.json
```

Metrics nhỏ:

```text
results/detection/top_yolov8n_baseline_metrics.csv
```

`summary.json` tối thiểu có:

```text
experiment_id
dataset
dataset_version
dataset manifest
model
epochs
batch
imgsz
seed
best_epoch
precision
recall
mAP50
mAP50_95
training_runtime_sec
best_model path
best_model SHA256
software versions
git commit
hardware
warnings
```

---

# 20. TOP EVALUATION

Reload:

```text
runs/top/yolov8n_top_v2_baseline/weights/best.pt
```

Validate độc lập.

Experiment:

```text
TOP_DET_YOLOV8N_EVAL_001
```

Evidence:

```text
logs/detection/TOP_DET_YOLOV8N_EVAL_001/
```

Results:

```text
results/detection/top_yolov8n_validation_metrics.csv
results/detection/top_yolov8n_reproducibility_check.csv
results/detection/top_yolov8n_count_diagnostics.csv
```

Tối thiểu:

```text
Precision
Recall
mAP50
mAP50-95
parameters
GFLOPs
model size MB
preprocess ms
inference ms
postprocess ms
validation runtime
validation image count
validation object count
```

Nếu có test split:

- có thể đánh giá thêm test;
- phải ghi rõ split;
- không trộn test metric với validation metric.

---

# 21. BẢNG SO SÁNH FRONT ↔ TOP

Notebook 14 phải sinh bảng nhỏ:

```text
results/detection/front_top_detection_comparison.csv
```

Cột gợi ý:

```text
camera
dataset_version
model
imgsz
epochs
batch
precision
recall
mAP50
mAP50_95
n_validation_images
n_validation_objects
parameters
GFLOPs
model_size_MB
inference_ms
```

FRONT reference:

```text
dataset_version = 1
model = yolov8n.pt
imgsz = 640
epochs = 100
batch = 16
precision = 0.9677949493
recall = 0.9664655248
mAP50 = 0.9898324652
mAP50_95 = 0.5525137653
validation_images = 254
validation_objects = 995
```

Không kết luận camera nào "tốt hơn" chỉ từ một metric.

---

# 22. TOP VIDEO INPUT CHO TRACKING

Tracking cần video TOP thật.

Codex phải tìm trong các vị trí repo-local hợp lệ, ví dụ:

```text
data/raw/top/
data/raw/top/T1/
data/raw/top/T2/
```

Không hard-code tên video nếu chưa thấy file.

Inventory:

```bash
find data/raw/top -type f \( -iname '*.mp4' -o -iname '*.avi' -o -iname '*.mov' \) | sort
```

Nếu không có video TOP:

- Notebook 14 vẫn có thể chuẩn bị phần detection;
- phần tracking phải có input validation và báo `MISSING TOP VIDEO`;
- không tạo fake tracking results;
- không dùng video FRONT để thay thế TOP.

---

# 23. TOP VIDEO DETECTION BASELINE

Sau detector validation:

Run trên một fixed TOP video.

Experiment ví dụ:

```text
TOP_VIDEO_DET_001
```

Local output:

```text
outputs/top/detection/
```

Ví dụ:

```text
detection_overlay.mp4
detection_per_frame.csv
```

Không commit overlay video.

Evidence nhỏ:

```text
results/detection/top_video_detection_summary.csv
logs/detection/TOP_VIDEO_DET_001/
```

Tối thiểu thống kê:

```text
mean detections/frame
median detections/frame
min
max
processing FPS
confidence threshold
iou threshold
video fps
video resolution
```

Nếu true fish count của video được biết chắc:

thêm:

```text
exact-count rate
undercount rate
overcount rate
count MAE
count RMSE
count bias
```

Nếu true count không chắc:

> Không giả định.

---

# 24. TOP TRACKER BASELINE

Tạo:

```text
configs/trackers/top_bytetrack_b15.yaml
```

Ban đầu copy chính xác:

```yaml
tracker_type: bytetrack
track_high_thresh: 0.68
track_low_thresh: 0.50
new_track_thresh: 0.68
track_buffer: 15
match_thresh: 0.80
fuse_score: true
```

Experiment:

```text
TOP_TRACK_BYTETRACK_B15_001
```

Mục đích:

> kiểm tra mức transfer của tracker setting đã chốt cho FRONT sang góc nhìn TOP.

Không gọi đây là tracker tối ưu TOP.

---

# 25. METRIC TRACKING TOP

Tối thiểu nếu chưa có MOT ground truth:

```text
mean tracks/frame
median tracks/frame
unique track IDs
median lifespan
mean lifespan
longest lifespan
short track count
gap events
processing FPS
```

Nếu biết đúng số cá:

```text
exact-count rate
count MAE
proliferation factor
```

Nhưng phải ghi:

> Đây là tracking diagnostics, chưa phải MOT identity accuracy chính thức.

Không gọi các metric này là:

```text
HOTA
IDF1
official MOT accuracy
```

nếu chưa có identity ground truth.

---

# 26. KHÔNG TUNING TRACKER TRƯỚC BASELINE

Sau `TOP_TRACK_BYTETRACK_B15_001`:

Notebook phải tổng kết.

Không tự động chạy:

```text
B30
B60
BoT-SORT
OC-SORT
```

trừ khi Notebook 14 đã được thiết kế và user phê duyệt phạm vi tuning.

Ưu tiên:

```text
baseline first
→ inspect failure
→ decide next experiment
```

Không thay detector và tracker cùng lúc.

---

# 27. OUTPUT TRACKING TOP

Local heavy:

```text
outputs/top/tracking/
```

Evidence:

```text
logs/tracking/TOP_TRACK_BYTETRACK_B15_001/
├── config.yaml
├── environment.txt
└── summary.json
```

Results:

```text
results/tracking/top_bytetrack_baseline_summary.csv
```

Nếu sinh trajectory per-frame lớn:

```text
outputs/top/tracking/top_tracking_raw.parquet
```

Không commit Parquet lớn.

---

# 28. NOTEBOOK 14 — KẾT LUẬN PHẢI DỪNG ĐÚNG PHẠM VI

Cuối Notebook 14 phải trả lời:

```text
1. TOP dataset V2 có hợp lệ không?
2. Dataset có mixed bbox/polygon không?
3. TOP YOLOv8n baseline đạt metric gì?
4. So với FRONT baseline khác biệt thế nào?
5. Fixed TOP video có lỗi detection gì?
6. ByteTrack B15 transfer baseline có đủ ổn định không?
7. Có cần tracker tuning cho TOP không?
8. Input trajectory đã đủ để chuyển Notebook 15 chưa?
```

Không kết luận:

```text
stress
happy
sick
disease
feeding
pair interaction
```

từ TOP nếu chưa có ground truth tương ứng.

---

# 29. CÁC FILE CODEx CÓ THỂ TẠO/SỬA TRONG TASK NÀY

Dự kiến hợp lệ:

```text
notebooks/14_top_detection_tracking.ipynb

configs/trackers/top_bytetrack_b15.yaml

logs/data/roboflow_versions.csv

logs/detection/TOP_DATASET_AUDIT_V2_001/...
logs/detection/TOP_DET_YOLOV8N_001/...
logs/detection/TOP_DET_YOLOV8N_EVAL_001/...
logs/detection/TOP_VIDEO_DET_001/...

logs/tracking/TOP_TRACK_BYTETRACK_B15_001/...

results/detection/top_dataset_audit_summary.csv
results/detection/top_class_distribution.csv
results/detection/top_dataset_manifest.json
results/detection/top_yolov8n_baseline_metrics.csv
results/detection/top_yolov8n_validation_metrics.csv
results/detection/front_top_detection_comparison.csv
results/detection/top_video_detection_summary.csv

results/tracking/top_bytetrack_baseline_summary.csv
```

Nhưng:

> Những file kết quả chỉ được tạo sau khi USER thực sự chạy Notebook 14 và có dữ liệu thật.

Codex không được tạo số liệu giả để lấp file.

---

# 30. CÁC FILE KHÔNG ĐƯỢC SỬA NẾU KHÔNG THẬT SỰ CẦN

Không thay đổi logic FRONT trong:

```text
notebooks/02_dataset_detection_audit.ipynb
notebooks/03_yolo_detection_training.ipynb
notebooks/04_yolo_detection_evaluation.ipynb
notebooks/05_front_video_detection.ipynb
notebooks/06_front_detection_failure_audit.ipynb
notebooks/07_front_bytetrack_ablation.ipynb
notebooks/08_front_tracker_benchmark.ipynb
notebooks/10_front_trajectory_cleaning.ipynb
notebooks/11_front_behavior_features.ipynb
notebooks/12_front_behavior_labeling.ipynb
notebooks/13_front_behavior_models.ipynb
```

Không sửa:

```text
configs/trackers/front_bytetrack_b15.yaml
```

để phục vụ TOP.

Tạo file TOP riêng.

---

# 31. DATA PATH POLICY

Dù máy hiện tại có:

```text
/home/diy-hus/fish
```

notebook không được hard-code path này.

Dùng:

```python
from pathlib import Path

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name == "notebooks":
    PROJECT_ROOT = PROJECT_ROOT.parent
PROJECT_ROOT = PROJECT_ROOT.resolve()
```

Sau đó:

```python
TOP_DATASET = PROJECT_ROOT / "data/roboflow/top_detect_v2"
```

Path cấu hình chung:

```text
configs/paths.yaml
```

---

# 32. GITIGNORE / DATA POLICY

Repo hiện ignore:

```text
data/raw/
data/roboflow/
data/processed/
data/eval/
models/
runs/
weights/
*.pt
*.onnx
*.engine
*.tflite
*.mp4
*.avi
*.mov
*.mkv
outputs/
artifacts_local/
.env
credentials*.json
token*.json
```

Do đó không force-add các file này.

Không dùng:

```bash
git add -f data/...
git add -f runs/...
git add -f *.pt
```

Evidence phải là CSV/JSON/log/plot nhỏ.

---

# 33. GIT CHECKPOINT CHO TOP

Chỉ sau khi:

- user đã Run Notebook 14;
- outputs được kiểm tra;
- metrics đúng;
- logs/results đầy đủ;
- user đồng ý commit;

mới chuẩn bị commit.

Tên checkpoint khuyến nghị:

```text
checkpoint-14-top-detection-tracking
```

Trước commit:

```bash
git status --short
git diff
git diff --cached
```

Đảm bảo không stage:

```text
dataset
video
weights
API key
secret
large output
```

Không push tự động nếu user chưa yêu cầu.

---

# 34. EDGE TPU / CORAL — CHƯA LÀ TASK HIỆN TẠI

Repo đã có FRONT demo:

```text
pi_front/
├── README_PI_FRONT_DEMO.md
├── export_front_edgetpu.py
├── fish_monitor.py
└── requirements_pi.txt
```

FRONT export hiện dùng:

```text
YOLO .pt
→ EdgeTPU TFLite
```

và demo dùng:

```text
YOLO detector on Coral
→ ByteTrack
→ trajectory cleaning
→ behavior features
→ Random Forest
```

### Nhưng với TOP hiện tại:

Không tạo `pi_top` trong Notebook 14.

Không export TOP EdgeTPU ngay.

Không benchmark Coral ngay.

Việc này dành cho Notebook 18 hoặc yêu cầu deployment riêng sau khi khoa học TOP đã chốt.

---

# 35. KHI SAU NÀY EXPORT TOP

Khi user yêu cầu export:

Dùng:

```bash
conda activate fish-export
```

Không dùng environment này để train.

Export phải lấy:

```text
runs/top/yolov8n_top_v2_baseline/weights/best.pt
```

hoặc model TOP final đã được chốt sau tuning.

Calibration data:

```text
data/roboflow/top_detect_v2/data.yaml
```

Không dùng FRONT dataset để calibration model TOP.

Có thể benchmark:

```text
imgsz 320
imgsz 512
```

nhưng chỉ sau khi có baseline scientific.

---

# 36. KHÔNG TỰ ÁP DỤNG 320×320 VÀO BASELINE TOP

Ý tưởng edge optimization sau này:

```text
detect 320×320
display 640×640 hoặc kích thước UI lớn hơn
```

là experiment deployment.

Không dùng 320 để thay `imgsz=640` trong TOP training baseline.

Trình tự đúng:

```text
TOP scientific baseline @ 640
→ validate
→ tracking
→ behavior
→ chốt pipeline
→ edge benchmark 320 vs 512/640
```

---

# 37. CHECKLIST TRƯỚC KHI CODEX TẠO NOTEBOOK 14

Codex phải xác nhận được:

```text
[ ] repo đúng khkt-tn/fish
[ ] branch/HEAD đã kiểm tra
[ ] AGENTS.md đã đọc
[ ] FISH_AI_PROJECT_WORKFLOW.md đã đọc
[ ] conda env fish tồn tại
[ ] Python interpreter thuộc env fish
[ ] TOP dataset version = 2
[ ] local root = data/roboflow/top_detect_v2
[ ] data.yaml tồn tại
[ ] class mapping đã đọc
[ ] không có blocker authentication
[ ] reference FRONT configs/results đã đọc
```

Nếu dataset chưa có:

> Dừng ở Roboflow download gate, không tạo notebook giả vờ input đã tồn tại.

---

# 38. CHECKLIST NOTEBOOK 14

Notebook phải có:

```text
[ ] Title
[ ] Scientific objective
[ ] Provenance
[ ] CONFIG
[ ] Project-root resolution
[ ] Environment validation
[ ] Dataset source/version validation
[ ] Dataset audit
[ ] Class distribution
[ ] Mixed bbox/polygon check
[ ] Duplicate/leakage check
[ ] YOLOv8n TOP baseline
[ ] Training log/evidence
[ ] Reloaded best-model validation
[ ] FRONT vs TOP comparison
[ ] TOP video discovery/input validation
[ ] TOP video detector diagnostics
[ ] ByteTrack B15 transfer baseline
[ ] Tracking diagnostics
[ ] Output paths
[ ] Warnings
[ ] Summary
[ ] Decision
[ ] Next step = user review before Notebook 15
```

---

# 39. SAU KHI CODEX CHUẨN BỊ NOTEBOOK 14

Codex phải báo theo format:

## A. Repository

```text
Branch:
HEAD:
Working tree:
Remote:
```

## B. Environment

```text
Conda env:
Python:
Torch:
CUDA:
GPU:
Ultralytics:
```

## C. Roboflow TOP

```text
Workspace: phys-hus
Project: fish-top-detection
Version: 2
Format: yolov8
Local root: data/roboflow/top_detect_v2
data.yaml: FOUND / MISSING
```

## D. Dataset pre-audit

```text
Train:
Valid:
Test:
Classes:
Warnings:
```

## E. Files created/modified

```text
...
```

## F. Notebook ready

Phải nói rõ:

```text
notebooks/14_top_detection_tracking.ipynb is prepared.
Please open it in VS Code with the fish kernel and Run All manually.
```

Sau đó:

> STOP.

---

# 40. SAU KHI USER RUN NOTEBOOK 14

Khi user báo đã chạy xong, Codex mới kiểm tra:

```text
notebook outputs
runs/top/
logs/detection/
logs/tracking/
results/detection/
results/tracking/
```

Kiểm tra lỗi trước khi commit evidence.

Báo cáo:

## Detection

```text
TOP Precision:
TOP Recall:
TOP mAP50:
TOP mAP50-95:
Best epoch:
Runtime:
Warnings:
```

## FRONT vs TOP

| Metric | FRONT | TOP |
|---|---:|---:|
| Precision | 0.9677949493 | |
| Recall | 0.9664655248 | |
| mAP50 | 0.9898324652 | |
| mAP50-95 | 0.5525137653 | |

## Tracking

```text
Tracker:
Video:
Mean tracks/frame:
Unique IDs:
Median lifespan:
Gap events:
FPS:
Known limitations:
```

## Decision

Một trong:

```text
PASS — ready for Notebook 15
PASS WITH WARNING — proceed but document limitations
HOLD — TOP detection/tracking requires correction first
```

---

# 41. TIÊU CHÍ ĐỂ CHUYỂN SANG NOTEBOOK 15

Không dùng một threshold mAP tùy ý để quyết định.

Notebook 15 chỉ bắt đầu khi:

```text
1. TOP detector chạy ổn định;
2. dataset provenance rõ;
3. tracking sinh trajectory dùng được;
4. failure modes đã được ghi;
5. không có lỗi class mapping nghiêm trọng;
6. không có lỗi dataset split nghiêm trọng chưa xử lý;
7. các experiment có log và summary;
8. user đã review Notebook 14.
```

Nếu tracking chưa hoàn hảo nhưng đủ tạo trajectory có kiểm soát:

có thể `PASS WITH WARNING`.

---

# 42. MỤC TIÊU KHOA HỌC CỦA TOP

TOP không chỉ nhằm tạo bbox.

Dữ liệu TOP phải phục vụ phân tích sau này:

```text
x-y movement
path length
speed
turning
space use
center/perimeter use
wall-following
group centroid
group spread
pairwise distance
nearest-neighbor distance
aggregation/dispersion
```

Do đó Notebook 14 phải giữ:

```text
frame index
timestamp
track_id
bbox
center x
center y
confidence
source video/session
tank/condition nếu biết
```

để Notebook 15 có thể tính feature.

---

# 43. RESEARCH PROVENANCE

Mỗi TOP experiment cần truy ngược:

```text
paper/result
↓
results/*.csv
↓
experiment_id
↓
logs/<stage>/<experiment_id>/summary.json
↓
notebook 14
↓
dataset version 2
↓
model SHA256
↓
git commit
```

Đây là yêu cầu bắt buộc.

---

# 44. NHỮNG ĐIỀU CODEX KHÔNG ĐƯỢC LÀM TRONG TASK NÀY

Không:

1. đổi Roboflow TOP version 2 thành version khác;
2. train bằng `fish-export`;
3. tạo Conda env mới;
4. upgrade broad packages;
5. tự Run Notebook 14;
6. chạy Notebook 15;
7. tạo TOP behavior model;
8. export Coral ngay;
9. sửa FRONT tracker;
10. sửa FRONT metrics;
11. ghi đè `runs/front`;
12. commit `.pt`;
13. commit dataset;
14. commit video;
15. lưu API key;
16. fake result CSV;
17. giả định Front ID == Top ID;
18. gọi px là cm nếu chưa calibration;
19. gọi tracking diagnostic là HOTA/IDF1 nếu chưa MOT GT;
20. push GitHub tự động.

---

# 45. THỨ TỰ THỰC HIỆN CHÍNH THỨC

Codex làm đúng:

```text
STEP 1
Audit Git/repository

STEP 2
Read AGENTS.md + workflow

STEP 3
Activate/check conda fish

STEP 4
Check TOP Roboflow V2 local dataset

STEP 5
If missing:
STOP for manual Roboflow Version 2 download

STEP 6
Audit TOP dataset

STEP 7
Prepare Notebook 14 using FRONT reference

STEP 8
Create TOP-specific tracker baseline config

STEP 9
Static review notebook

STEP 10
Report notebook ready

STEP 11
STOP — user Run All manually

STEP 12
After user run:
verify real outputs

STEP 13
Generate/finalize logs + results evidence

STEP 14
Compare FRONT vs TOP

STEP 15
Recommend PASS / PASS WITH WARNING / HOLD

STEP 16
STOP for user approval

STEP 17
Only after approval:
commit checkpoint-14-top-detection-tracking

STEP 18
Only after approval:
move to Notebook 15
```

---

# 46. FINAL INSTRUCTION TO CODEX

Do not treat this as a greenfield object-detection project.

This repository already contains a completed FRONT scientific pipeline and a defined experimental workflow.

Your task is to:

> **extend the existing research provenance from FRONT to TOP, beginning with Roboflow TOP dataset Version 2 and Notebook 14, while preserving matched detector conditions and independently validating TOP tracking.**

The most important constraints are:

```text
FRONT = reference
TOP Roboflow = phys-hus / fish-top-detection / version 2
TOP local = data/roboflow/top_detect_v2
training environment = fish
export environment = fish-export, later only
baseline detector = yolov8n.pt
imgsz = 640
epochs = 100
batch = 16
seed = 42
Notebook 14 must be run manually by the user
no cross-camera ID assumption
no automatic push
```

Stop after preparing Notebook 14 and wait for the user to run it.
