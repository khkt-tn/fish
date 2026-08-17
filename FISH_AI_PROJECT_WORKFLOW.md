# FISH AI PROJECT — QUY TRÌNH THỰC NGHIỆM TỪ ĐẦU ĐẾN CUỐI

## 0. Mục tiêu của tài liệu

Tài liệu này là **quy trình chuẩn duy nhất** để triển khai, quản lý và tái lập toàn bộ dự án nghiên cứu hành vi cá bằng AI trên máy mới.

Môi trường làm việc dự kiến:

- Windows + WSL
- VS Code
- Anaconda / Conda
- Conda environment: `fish`
- GPU NVIDIA nếu có
- Dữ liệu thô gốc: lưu trữ lâu dài trên Google Drive; user tự tải/copy thủ công vào local khi cần
- Dataset detection đã gán nhãn: Roboflow là source-of-truth
- GitHub: chỉ quản lý source code, notebook, cấu hình, log, bảng kết quả nhỏ và tài liệu
- Dữ liệu/video/model/output nặng: **không commit lên GitHub**

Mục tiêu khoa học tổng quát:

```text
Dữ liệu video Front / Top
        ↓
Dataset + ground truth
        ↓
YOLO detection
        ↓
Tracking
        ↓
Trajectory
        ↓
Behavioral features
        ↓
Behavior classification
        ↓
Đồng bộ cảm biến môi trường
        ↓
Phân tích môi trường ↔ hành vi cá
        ↓
Triển khai mô hình nhẹ trên Raspberry Pi
```

---

# 1. Nguyên tắc quản lý dự án

## 1.1. Ba lớp dữ liệu

### A. Source of truth — KHÔNG phụ thuộc máy cá nhân

**Google Drive**
- archival source-of-truth cho dữ liệu thô gốc;
- video thô;
- dữ liệu cảm biến thô;
- dữ liệu thu thập gốc;
- video thí nghiệm;
- các file lớn cần lưu lâu dài.
- không tích hợp authentication hoặc download tự động vào pipeline chuẩn;
- user tự tải/copy file cần thiết vào `data/raw/`.

**Roboflow**
- source-of-truth cho labeled detection datasets;
- ảnh đã gán bounding box;
- phiên bản dataset detection;
- train / valid / test split;
- lịch sử các phiên bản dataset.

Hai nguồn trên phải đủ để tải lại toàn bộ dữ liệu cần thiết nếu máy cá nhân bị xóa.

### B. Local working data — có thể xóa sau dự án

Ví dụ:

```text
data/
models/
outputs/
runs/
artifacts_local/
```

Các thư mục này:
- là working copy do user tải/copy thủ công từ Drive, lấy từ đúng Roboflow dataset version, hoặc do notebook sinh ra;
- không phải nguồn lưu trữ duy nhất;
- được `.gitignore` và không commit Git;
- có thể xóa sau khi dự án kết thúc để giải phóng bộ nhớ.

### C. Research evidence — PHẢI quản lý bằng Git

Commit lên GitHub:

```text
notebooks/
scripts/
src/
configs/
logs/
results/
docs/
README.md
environment/
```

Trong đó lưu:
- notebook đã chạy;
- config chính xác của từng experiment;
- log;
- bảng CSV nhỏ;
- biểu đồ nhỏ;
- summary JSON/CSV;
- metric;
- model SHA-256;
- dataset version;
- git commit;
- thời điểm chạy;
- phiên bản Python / PyTorch / Ultralytics / CUDA.

---

# 2. Cấu trúc repository chuẩn

Đề nghị tạo repository:

```text
fish/
├── README.md
├── FISH_AI_PROJECT_WORKFLOW.md
├── .gitignore
│
├── notebooks/
│   ├── 00_environment_check.ipynb
│   ├── 01_data_source_inventory.ipynb
│   ├── 02_dataset_detection_audit.ipynb
│   ├── 03_yolo_detection_training.ipynb
│   ├── 04_yolo_detection_evaluation.ipynb
│   ├── 05_front_video_detection.ipynb
│   ├── 06_front_detection_failure_audit.ipynb
│   ├── 07_front_bytetrack_ablation.ipynb
│   ├── 08_front_tracker_benchmark.ipynb
│   ├── 09_front_mot_groundtruth_eval.ipynb
│   ├── 10_front_trajectory_cleaning.ipynb
│   ├── 11_front_behavior_features.ipynb
│   ├── 12_front_behavior_labeling.ipynb
│   ├── 13_front_behavior_models.ipynb
│   ├── 14_top_detection_tracking.ipynb
│   ├── 15_top_behavior_features.ipynb
│   ├── 16_sensor_sync.ipynb
│   ├── 17_environment_behavior_analysis.ipynb
│   ├── 18_raspberrypi_export_benchmark.ipynb
│   └── 19_final_results.ipynb
│
├── src/
│   ├── detection/
│   ├── tracking/
│   ├── behavior/
│   ├── sensors/
│   └── utils/
│
├── scripts/
│   ├── download_roboflow_data.sh
│   ├── run_front_detection.py
│   ├── run_front_tracking.py
│   └── ...
│
├── configs/
│   ├── paths.yaml
│   ├── data_sources.yaml
│   ├── detection/
│   ├── tracking/
│   └── behavior/
│
├── logs/
│   ├── environment/
│   ├── detection/
│   ├── tracking/
│   ├── behavior/
│   └── deployment/
│
├── results/
│   ├── detection/
│   ├── tracking/
│   ├── behavior/
│   └── final/
│
├── docs/
│   ├── EXPERIMENT_RULES.md
│   ├── DATA_DICTIONARY.md
│   └── ANNOTATION_GUIDE.md
│
├── environment/
│   ├── environment.yml
│   └── pip_freeze.txt
│
├── data/                     # KHÔNG GIT
│   ├── raw/
│   ├── roboflow/
│   ├── processed/
│   └── eval/
│
├── models/                   # KHÔNG GIT
├── runs/                     # KHÔNG GIT
├── outputs/                  # KHÔNG GIT, trừ summary nhỏ được copy sang results/
└── artifacts_local/          # KHÔNG GIT
```

---

# 3. `.gitignore` bắt buộc

Tạo `.gitignore` tối thiểu:

```gitignore
# Python
__pycache__/
*.pyc
.ipynb_checkpoints/

# Conda / environment
.conda/
.venv/
venv/

# Raw / downloaded data
data/raw/
data/roboflow/
data/processed/
data/eval/

# Models / training outputs
models/
runs/
weights/
*.pt
*.onnx
*.engine
*.tflite

# Video / large media
*.mp4
*.avi
*.mov
*.mkv

# Local artifacts
outputs/
artifacts_local/

# Temporary files
*.tmp
*.cache
*.log.tmp

# Secrets
.env
*.key
credentials*.json
token*.json
```

Lưu ý:

- `logs/` **không ignore**.
- `results/` **không ignore**.
- notebook **không ignore**.
- không commit token Roboflow / Drive / GitHub.

---

# 4. Khởi tạo máy mới

## Notebook 00 — `00_environment_check.ipynb`

Mục tiêu:
- xác nhận Python;
- xác nhận Conda env `fish`;
- xác nhận PyTorch;
- CUDA;
- GPU;
- Ultralytics;
- OpenCV;
- NumPy;
- pandas;
- matplotlib;
- notebook kernel.

Các thông tin phải log:

```text
date/time
hostname
OS / WSL
Python
Conda environment
PyTorch
CUDA runtime
CUDA available
GPU
Ultralytics
OpenCV
NumPy
pandas
matplotlib
```

Ví dụ kiểm tra:

```python
import sys
import torch
import ultralytics
import cv2
import numpy as np
import pandas as pd
import matplotlib

print("Python:", sys.version)
print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

print("Ultralytics:", ultralytics.__version__)
print("OpenCV:", cv2.__version__)
print("NumPy:", np.__version__)
print("pandas:", pd.__version__)
print("matplotlib:", matplotlib.__version__)
```

Xuất:

```text
logs/environment/environment_YYYYMMDD_HHMM.txt
environment/pip_freeze.txt
environment/environment.yml
```

Lệnh:

```bash
conda env export --from-history > environment/environment.yml
pip freeze > environment/pip_freeze.txt
```

Commit checkpoint:

```text
checkpoint-00-environment
```

---

# 5. Quản lý đường dẫn

Không hard-code đường dẫn máy cũ như:

```text
/home/diy-hus/fish/...
```

Dùng đường dẫn tương đối theo repository.

Ví dụ `configs/paths.yaml`:

```yaml
project_root: .

data:
  raw: data/raw
  roboflow: data/roboflow
  processed: data/processed
  eval: data/eval

models: models
runs: runs
outputs: outputs
logs: logs
results: results
```

Trong notebook:

```python
from pathlib import Path

PROJECT_ROOT = Path.cwd()

if PROJECT_ROOT.name == "notebooks":
    PROJECT_ROOT = PROJECT_ROOT.parent

DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = PROJECT_ROOT / "logs"
RESULTS_DIR = PROJECT_ROOT / "results"
```

Mục tiêu:
- đổi máy không phải sửa toàn bộ notebook;
- sau khi xóa dữ liệu local, tải lại đúng chỗ là chạy được.

---

# 6. Nguồn dữ liệu thô và inventory local

## Nguyên tắc

Google Drive là archival source-of-truth giữ:

```text
raw video
sensor raw data
original experiment data
```

Local:

```text
data/raw/
```

Ví dụ:

```text
data/raw/
├── front/
│   ├── T1/
│   └── T2/
├── top/
│   ├── T1/
│   └── T2/
└── sensors/
```

Không copy dữ liệu thô vào Git.

Khi cần raw video hoặc sensor data, user tự download/copy thủ công file cần thiết từ Google Drive vào `data/raw/`.

Pipeline chuẩn:
- không login Google Drive;
- không yêu cầu Google Drive authentication;
- không download tự động;
- không phụ thuộc `rclone`.

`rclone` chỉ là optional utility nếu sau này user chủ động muốn dùng. Việc cài đặt, OAuth và cấu hình `rclone` không thuộc workflow chuẩn và phải tuân thủ authentication stop gate.

## Notebook 01 — `01_data_source_inventory.ipynb`

Notebook 01 không login, không download tự động và không chạy Roboflow API.

Notebook đọc `configs/data_sources.yaml` và chỉ inventory các file đã có trong local working copy.

Notebook phải:
- validate cấu hình nguồn dữ liệu;
- quét các đường dẫn local đã khai báo;
- ghi relative path và kích thước file;
- tính SHA-256 checksum;
- với video, đọc duration, FPS, resolution và số frame khi có thể;
- đối chiếu file hiện có với các input bắt buộc trong config;
- báo rõ dữ liệu nào còn thiếu để Notebook 02 hoặc bước tiếp theo chạy được;
- không lưu video hoặc dữ liệu lớn trong notebook.

Input cấu hình:

```text
configs/data_sources.yaml
```

Xuất:

```text
logs/data/data_source_inventory.csv
```

Các cột:

```text
source
source_of_truth
relative_path
exists
required_for_next_step
file_size
sha256
video_fps
video_frames
duration_sec
width
height
```

---

# 7. Labeled detection datasets trên Roboflow

Roboflow là source-of-truth cho dataset detection đã gán nhãn, các dataset version và train/validation/test split.

Notebook 01 không gọi Roboflow API và chỉ inventory một local working copy nếu nó đã tồn tại. Việc restore/download đúng dataset version là bước riêng, chỉ thực hiện khi user phê duyệt và sau mọi authentication stop gate cần thiết.

Mỗi lần dùng một version phải log:

```text
workspace
project
version
format
download_date
local_path
```

Ví dụ local:

```text
data/roboflow/front_detect_v1/
data/roboflow/top_detect_v1/
```

Không commit toàn bộ dataset.

Commit duy nhất metadata:

```text
logs/data/roboflow_versions.csv
```

Ví dụ:

```csv
camera,project,version,format,local_path
front,fish-front,1,yolov8,data/roboflow/front_detect_v1
top,fish-top,1,yolov8,data/roboflow/top_detect_v1
```

---

# 8. Dataset audit

## Notebook 02 — `02_dataset_detection_audit.ipynb`

Kiểm tra:

```text
train / valid / test
số ảnh
số bbox
class distribution
ảnh lỗi
label lỗi
bbox ngoài ảnh
ảnh không label
duplicate
resolution
tank T1/T2
background
camera
```

Mục tiêu:
- hiểu dataset trước train;
- tạo bằng chứng về chất lượng dữ liệu.

Xuất:

```text
results/detection/dataset_audit_summary.csv
results/detection/dataset_class_distribution.csv
logs/detection/dataset_audit.log
```

---

# 9. Train YOLO

## Notebook 03 — `03_yolo_detection_training.ipynb`

Nguyên tắc:

Mỗi experiment có một `run_id`.

Ví dụ:

```text
FRONT_DET_001
FRONT_DET_002
```

Mỗi run phải lưu:

```text
model name
dataset version
epochs
imgsz
batch
optimizer
seed
device
training time
best epoch
best.pt SHA-256
git commit hash
```

Không dựa vào tên folder mặc định của Ultralytics làm evidence duy nhất.

Cấu trúc log:

```text
logs/detection/FRONT_DET_001/
├── config.yaml
├── environment.txt
├── summary.json
└── train.log
```

Copy bảng metric nhỏ sang:

```text
results/detection/
```

Không commit:

```text
runs/
best.pt
last.pt
```

---

# 10. Đánh giá detection

## Notebook 04 — `04_yolo_detection_evaluation.ipynb`

So sánh các model YOLO nhỏ phù hợp triển khai edge.

Metric tối thiểu:

```text
Precision
Recall
mAP50
mAP50-95
parameters
GFLOPs
model size
inference FPS
```

Sau này có thể thêm:

```text
Raspberry Pi FPS
latency
RAM
CPU utilization
```

Bảng cuối:

```text
results/detection/model_comparison.csv
```

---

# 11. Detection trên video Front

## Notebook 05 — `05_front_video_detection.ipynb`

Đây là checkpoint hiện dự án đã làm được trên máy cũ.

Input:

```text
video Front
best.pt
```

Output local:

```text
outputs/front/detection/
├── detection_overlay.mp4
└── detection_per_frame.csv
```

Evidence Git:

```text
results/detection/front_video_detection_summary.csv
logs/detection/front_video_detection.log
```

Không commit video overlay.

---

# 12. Detection-only failure audit

## Notebook 06 — `06_front_detection_failure_audit.ipynb`

Với video có **8 cá thật**:

Đã dùng các metric:

```text
mean detections/frame
median
min/max
exact-count rate
undercount rate
overcount rate
count MAE
count RMSE
mean count bias
```

Các experiment quan trọng đã có:

```text
D025 — conf = 0.25
D010 — conf = 0.10
```

Tạo thư mục ảnh local:

```text
outputs/front/failure_audit/
├── severe_under/
├── under/
├── exact/
└── over/
```

Phân loại lỗi:

```text
occlusion
obstacle
miss
merge
duplicate
false_positive
```

Evidence:

```text
results/detection/front_detection_failure_summary.csv
```

---

# 13. ByteTrack ablation

## Notebook 07 — `07_front_bytetrack_ablation.ipynb`

Baseline đã có:

```text
B0:
conf = 0.25
track_buffer = 30

B1:
conf = 0.10
track_buffer = 30

B2:
conf = 0.10
track_buffer = 60
```

B1 hiện là ByteTrack baseline tốt nhất.

Không tiếp tục B3 nếu B2 không cải thiện continuity.

Metric:

```text
mean tracks/frame
exact 8-fish rate
count MAE
unique track IDs
proliferation factor
median lifespan
mean lifespan
longest lifespan
IDs <=1 s
IDs <=2 s
IDs >=5 s
IDs >=10 s
IDs with gaps
total gap events
missing frames
processing FPS
```

Evidence:

```text
results/tracking/bytetrack_ablation_summary.csv
logs/tracking/bytetrack_ablation.log
```

---

# 14. Benchmark tracker

## Notebook 08 — `08_front_tracker_benchmark.ipynb`

Các tracker:

```text
T1 ByteTrack B1
T2 BoT-SORT default
T3 OC-SORT default
```

Giữ:

```text
CONF = 0.10
IOU = 0.70
IMGSZ = 640
same model
same video
```

Các kết quả hiện tại cho thấy:

```text
BoT-SORT:
continuity cân bằng tốt nhất

ByteTrack:
FPS tốt nhất / phù hợp real-time hơn

OC-SORT:
unique ID thấp nhẹ nhưng gap lớn
```

Chưa coi đây là MOT accuracy chính thức.

Evidence:

```text
results/tracking/tracker_benchmark_summary.csv
```

---

# 15. MOT ground truth

## Notebook 09 — `09_front_mot_groundtruth_eval.ipynb`

Tạo 3 clip:

```text
E1_easy
E2_crossing
E3_obstacle
```

Mỗi clip:

```text
8–10 s
frame liên tục
```

Ground-truth identity:

```text
fish_01
fish_02
...
fish_08
```

Không dùng prediction tracker làm ground truth.

Metric chính thức:

```text
HOTA
IDF1
ID switches
fragmentation
```

Nếu identity không thể chắc chắn sau che khuất:

```text
ambiguous
```

không đoán.

Evidence:

```text
results/tracking/mot_official_metrics.csv
docs/ANNOTATION_GUIDE.md
```

---

# 16. Chốt detector + tracker

Sau notebook 09 mới quyết định cấu hình chính thức.

Ví dụ:

```text
DETECTOR_FINAL
TRACKER_FINAL
```

Ghi vào:

```text
configs/final_pipeline.yaml
```

File phải chứa:

```yaml
detector:
  model:
  dataset_version:
  conf:
  iou:
  imgsz:

tracker:
  name:
  config:

video:
  fps:

behavior:
  window_seconds:
```

---

# 17. Làm sạch trajectory

## Notebook 10 — `10_front_trajectory_cleaning.ipynb`

Input:

```text
frame
time
track_id
bbox
cx
cy
```

Xử lý:

```text
trajectory
↓
gap check
↓
remove invalid tracklets
↓
short smoothing
↓
normalized coordinates
```

Không smoothing quá mạnh.

Xuất local:

```text
outputs/front/trajectory/front_tracking_clean.parquet
```

Evidence nhỏ:

```text
results/tracking/trajectory_cleaning_summary.csv
```

---

# 18. Đặc trưng hành vi Front

## Notebook 11 — `11_front_behavior_features.ipynb`

Front ưu tiên:

```text
speed
path length
vertical position
vertical velocity
vertical range
surface ratio
middle ratio
bottom ratio
stop duration
burst frequency
```

Zone:

```text
surface
middle
bottom
```

Không kết luận `stress`.

---

# 19. Window hành vi

Dùng window:

```text
5 s
```

và bước:

```text
1 s
```

Ví dụ feature:

```text
mean_speed
median_speed
max_speed
std_speed
path_length
vertical_range
surface_ratio
middle_ratio
bottom_ratio
mean_vertical_velocity
```

Output:

```text
outputs/front/behavior/front_window_features.parquet
```

Evidence:

```text
results/behavior/front_feature_summary.csv
```

---

# 20. Gán nhãn hành vi

## Notebook 12 — `12_front_behavior_labeling.ipynb`

Các lớp ban đầu:

### Activity

```text
low_activity
normal_activity
rapid_activity
```

### Vertical zone

```text
surface
middle
bottom
```

### Vertical movement

```text
upward
downward
vertical_stable
```

Không dùng:

```text
stress
happy
sick
```

nếu chưa có ground truth sinh học.

---

# 21. Behavior model

## Notebook 13 — `13_front_behavior_models.ipynb`

So sánh:

```text
Rule-based
Random Forest
XGBoost
Temporal model nếu thật sự cần
```

Metric:

```text
Accuracy
Precision
Recall
F1
Confusion matrix
latency
```

Tách:

```text
train
validation
test
```

Không dùng cùng video trong train và test.

---

# 22. Camera Top

## Notebook 14–15

Top xử lý độc lập trước.

Top ưu tiên:

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

Không giả định:

```text
Front ID 3 == Top ID 3
```

Ghép hai camera theo thời gian trước khi nghĩ đến cross-camera identity.

---

# 23. Sensor synchronization

## Notebook 16 — `16_sensor_sync.ipynb`

Đồng bộ:

```text
video timestamp
sensor timestamp
```

Sensor:

```text
temperature
pH
light
...
```

Output:

```text
time
behavior features
environment variables
```

---

# 24. Phân tích môi trường ↔ hành vi

## Notebook 17 — `17_environment_behavior_analysis.ipynb`

Mục tiêu:

```text
environment condition
        ↓
behavioral response metrics
```

Ưu tiên báo cáo:

```text
effect size
distribution
confidence interval
correlation / regression
repeated measures nếu phù hợp
```

Không chỉ báo p-value.

---

# 25. Raspberry Pi deployment

## Notebook 18 — `18_raspberrypi_export_benchmark.ipynb`

Chỉ làm sau khi pipeline khoa học đã chốt.

So sánh:

```text
model format
model size
FPS
latency
CPU
RAM
power nếu đo được
```

Pipeline cuối:

```text
Camera
↓
YOLO lightweight
↓
tracker
↓
trajectory buffer
↓
feature window
↓
behavior model
↓
summary/event log
```

Không cần CSV làm trung gian trong real-time.

---

# 26. Tổng hợp kết quả

## Notebook 19 — `19_final_results.ipynb`

Notebook cuối chỉ đọc các file trong:

```text
results/
```

Không train.
Không xử lý video.

Sinh:

```text
Detection comparison table
Tracker comparison table
MOT official table
Behavior model table
Environment-behavior plots
Raspberry Pi benchmark table
```

Đây là nguồn trực tiếp để đưa số liệu vào bài nghiên cứu.

---

# 27. Quy tắc cho mỗi experiment

Mỗi experiment phải có:

```text
experiment_id
date/time
purpose
input source
dataset version
model
model SHA-256
configuration
seed
software versions
git commit
hardware
runtime
metrics
output paths
notes
```

Ví dụ `summary.json`:

```json
{
  "experiment_id": "FRONT_TRACK_BOTSORT_001",
  "purpose": "BoT-SORT benchmark",
  "video": "videos/8.mp4",
  "true_fish_count": 8,
  "model": "yolov8n_front_v1",
  "model_sha256": "...",
  "conf": 0.10,
  "iou": 0.70,
  "tracker": "botsort",
  "ultralytics": "8.4.120",
  "python": "3.11",
  "gpu": "...",
  "git_commit": "...",
  "metrics": {}
}
```

---

# 28. Git workflow đề nghị

Trước experiment:

```bash
git status
git pull
```

Sau khi notebook + log hoàn chỉnh:

```bash
git add notebooks/ logs/ results/ configs/ docs/
git commit -m "exp: FRONT_TRACK_BOTSORT_001"
git push
```

Không commit:

```text
raw video
downloaded dataset
weights
overlay video
large parquet
training cache
```

---

# 29. Notebook nên lưu output đến mức nào?

Nên commit notebook có:

```text
summary table
metric
small plots
short textual output
```

Không nhúng:

```text
video
hàng nghìn ảnh
DataFrame hàng trăm nghìn dòng
binary lớn
```

Nếu notebook quá lớn:
- xóa output nặng;
- giữ bảng tổng hợp;
- lưu full CSV local;
- copy summary CSV sang `results/`.

Mục tiêu:

> GitHub chứa bằng chứng khoa học đủ để hiểu experiment, nhưng không trở thành nơi lưu dataset.

---

# 30. Log là bằng chứng thực nghiệm

Không chỉ giữ notebook.

Mỗi experiment cần ít nhất:

```text
logs/<stage>/<experiment_id>/summary.json
```

Nên có thêm:

```text
config.yaml
environment.txt
stdout.log
```

Khi viết bài, mọi bảng số liệu phải có thể truy ngược:

```text
paper table
↓
results/*.csv
↓
experiment_id
↓
logs/
↓
notebook
↓
git commit
```

Đây là chuỗi provenance cần giữ.

---

# 31. Xóa dữ liệu local sau khi dự án hoàn tất

Chỉ xóa khi đã xác nhận:

- dữ liệu thô còn trên Drive;
- dataset còn trên Roboflow;
- model cuối đã backup ở nơi lưu trữ lâu dài;
- các file `results/`, `logs/`, `notebooks/`, `configs/` đã push GitHub;
- checksum / metadata đã lưu.

Các thư mục có thể xóa local:

```text
data/raw/
data/roboflow/
data/processed/
data/eval/
runs/
outputs/
models/       # chỉ sau khi đã backup model cần giữ
artifacts_local/
```

Sau này chỉ cần:

```text
git clone
conda env create
user tải/copy thủ công raw data cần thiết từ Drive
restore đúng Roboflow dataset version khi được phê duyệt
```

là tái lập được dự án.

---

# 32. Quy tắc backup model

Không để `best.pt` chỉ tồn tại trong:

```text
runs/
```

Mỗi model được chọn cần:

```text
model file
SHA-256
experiment ID
dataset version
metrics
```

Backup model cuối vào Drive, ví dụ:

```text
Fish_AI_Project/
└── models_archive/
    ├── front_detector_final.pt
    ├── top_detector_final.pt
    └── model_manifest.csv
```

GitHub chỉ lưu:

```text
model_manifest.csv
```

không lưu model binary nếu file lớn.

---

# 33. Các checkpoint Git quan trọng

Đề nghị:

```text
checkpoint-00-environment
checkpoint-01-data-source-inventory
checkpoint-02-dataset-audit
checkpoint-03-detection-trained
checkpoint-04-detection-evaluated
checkpoint-05-front-detection-video
checkpoint-06-detection-failure-audit
checkpoint-07-bytetrack-ablation
checkpoint-08-tracker-benchmark
checkpoint-09-mot-official-eval
checkpoint-10-final-tracker
checkpoint-11-front-features
checkpoint-12-behavior-dataset
checkpoint-13-behavior-model
checkpoint-14-top-pipeline
checkpoint-15-sensor-sync
checkpoint-16-environment-analysis
checkpoint-17-raspberrypi
checkpoint-18-final-results
```

---

# 34. Thứ tự thực hiện trên máy mới

## Phase A — Rebuild

```text
[ ] Clone / tạo repository fish
[ ] Đặt FISH_AI_PROJECT_WORKFLOW.md ở root
[ ] Kích hoạt conda fish
[ ] Chạy Notebook 00
[ ] Lưu environment.yml + pip_freeze
[ ] Tạo .gitignore
[ ] Tạo configs/paths.yaml
```

## Phase B — Restore data

```text
[ ] USER tải/copy thủ công raw video cần dùng từ Drive vào data/raw/
[ ] Restore đúng Roboflow dataset versions khi được phê duyệt
[ ] USER chạy Notebook 01 data source inventory thủ công trong VS Code
[ ] Chạy Notebook 02 dataset audit
```

## Phase C — Reproduce detection

```text
[ ] Notebook 03 train / hoặc restore best model
[ ] Notebook 04 validate detector
[ ] Notebook 05 video detection
[ ] Notebook 06 failure audit
```

## Phase D — Reproduce tracking

```text
[ ] Notebook 07 ByteTrack ablation
[ ] Notebook 08 tracker benchmark
[ ] Notebook 09 MOT evaluation
[ ] Chốt detector + tracker
```

## Phase E — Behavior

```text
[ ] Notebook 10 trajectory
[ ] Notebook 11 features
[ ] Notebook 12 labels
[ ] Notebook 13 behavior models
```

## Phase F — Top + sensors

```text
[ ] Notebook 14 Top tracking
[ ] Notebook 15 Top features
[ ] Notebook 16 sensor sync
[ ] Notebook 17 environment-behavior
```

## Phase G — Deployment and paper

```text
[ ] Notebook 18 Raspberry Pi
[ ] Notebook 19 final results
[ ] Push toàn bộ evidence GitHub
[ ] Backup model cuối
[ ] Xóa local heavy data nếu muốn
```

---

# 35. Việc nên làm NGAY trên máy mới

Không bắt đầu bằng tracking.

Thứ tự chính xác:

```text
1. Chuẩn hóa repository
2. Chạy environment check
3. Chuẩn hóa paths
4. USER tải/copy thủ công một phần raw data nhỏ nếu bước kế tiếp cần
5. USER chạy Notebook 01 để inventory local và xác nhận dữ liệu còn thiếu
6. Restore dataset Roboflow cần thiết khi được phê duyệt
7. Reproduce YOLO validation
8. Reproduce video detection
9. Sau khi detection giống máy cũ mới chạy tracking
```

Checkpoint đầu tiên cần đạt:

```text
Cùng best.pt
+
cùng validation set
+
cùng phần mềm đã log
→ metric detection tái lập gần với kết quả máy cũ
```

Sau đó mới tiếp tục tracking.

---

# 36. Nguyên tắc khoa học xuyên suốt

1. Không thay nhiều biến trong một ablation.
2. Không dùng cùng video để vừa train vừa test.
3. Không chọn model chỉ vì overlay nhìn đẹp.
4. Không gọi diagnostic là accuracy nếu chưa có ground truth.
5. Không gọi trạng thái hành vi là `stress` nếu chưa có cơ sở sinh học.
6. Không coi `track_id` là danh tính vĩnh viễn nếu chưa được chứng minh.
7. Mọi con số trong bài phải truy ngược được tới experiment.
8. Mọi experiment phải tái lập được từ notebook + config + source data.
9. Dữ liệu thô có thể xóa khỏi máy, nhưng không được mất source-of-truth.
10. GitHub quản lý **bằng chứng thực nghiệm**, không phải kho dữ liệu thô.

---

# 37. Quy ước tên experiment

Khuyến nghị:

```text
<CAMERA>_<STAGE>_<METHOD>_<NUMBER>
```

Ví dụ:

```text
FRONT_DET_YOLOV8N_001
FRONT_DET_CONF_001
FRONT_TRACK_BYTETRACK_001
FRONT_TRACK_BOTSORT_001
FRONT_MOT_EVAL_001
FRONT_BEHAV_RF_001
TOP_TRACK_BOTSORT_001
PI_BENCH_YOLOV8N_001
```

Tên experiment không được đổi sau khi đã commit.

---

# 38. Trạng thái dự án hiện tại cần tái lập

Các bước trước đây đã hoàn thành tới:

```text
YOLO fish detection
↓
detection-only audit
↓
ByteTrack ablation
↓
ByteTrack / BoT-SORT / OC-SORT benchmark
```

Nhưng trên máy mới, không nên copy ngẫu nhiên kết quả rồi chạy tiếp.

Cần:

```text
rebuild environment
↓
restore data
↓
restore / reproduce detector
↓
reproduce detection result
↓
reproduce tracking experiments
↓
tiếp tục MOT ground truth
↓
behavior
```

Mục tiêu là biến quá trình đã làm thành **pipeline nghiên cứu có provenance rõ ràng**, chứ không chỉ khôi phục code.

---

# 39. Definition of Done của dự án

Dự án chỉ được coi là hoàn chỉnh khi có:

### Detection

```text
dataset versions
training experiment logs
validation metrics
video failure audit
model comparison
```

### Tracking

```text
tracker ablation
tracker benchmark
MOT ground truth
HOTA / IDF1 / IDSW
```

### Behavior

```text
behavior definition
feature dataset
ground truth
model comparison
confusion matrix
```

### Environment

```text
sensor synchronization
statistical analysis
environment-behavior results
```

### Deployment

```text
Raspberry Pi benchmark
latency
FPS
resource usage
```

### Reproducibility

```text
GitHub repository
notebooks
logs
configs
results
environment file
Drive archival source
Roboflow labeled-dataset source
model archive
```

---

# 40. Tóm tắt kiến trúc quản lý

```text
                    ┌─────────────────────┐
                    │    GOOGLE DRIVE     │
                    │ archival raw source │
                    └──────────┬──────────┘
                               │ USER manual download/copy
                               ▼
                    ┌─────────────────────┐
                    │     LOCAL WSL       │
                    │ data/raw            │
                    └─────────────────────┘

                    ┌─────────────────────┐
                    │      ROBOFLOW       │
                    │ labeled source-of-  │
                    │ truth datasets      │
                    └──────────┬──────────┘
                               │ approved dataset restore
                               ▼
                    ┌─────────────────────┐
                    │ data/roboflow       │
                    └─────────────────────┘

                               │
                               ▼
                     NOTEBOOK EXPERIMENTS
                               │
                 ┌─────────────┼──────────────┐
                 ▼             ▼              ▼
              logs/         results/       outputs/
                 │             │              │
                 │             │              └── local, heavy
                 │             │
                 └──────┬──────┘
                        ▼
                      GITHUB
              notebook + log + result
                 + config + docs

Sau khi dự án kết thúc:

local heavy data → có thể xóa
GitHub evidence  → giữ
Drive raw data   → giữ
Roboflow dataset → giữ
final model      → backup Drive
```

---

## Kết luận

Từ máy mới, hãy coi repository Git là **sổ thí nghiệm điện tử** của dự án.

Mỗi notebook là một bước thực nghiệm độc lập.

Mỗi experiment phải tạo:

```text
notebook
+
config
+
log
+
summary
+
git commit
```

Dữ liệu lớn chỉ là tài nguyên tạm trên máy:

```text
Drive / Roboflow
      ↓
USER manual raw copy / approved dataset restore
      ↓
experiment
      ↓
evidence → GitHub
      ↓
xóa local nếu cần
```

Như vậy khi dự án kết thúc, bạn có thể xóa hàng chục hoặc hàng trăm GB dữ liệu trên máy mà vẫn giữ đầy đủ khả năng **truy xuất nguồn dữ liệu, kiểm chứng kết quả và tái lập thực nghiệm**.
