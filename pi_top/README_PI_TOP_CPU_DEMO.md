# Demo CPU CAMERA TOP trên Raspberry Pi 4

Đây là demo CAMERA TOP dùng **video đã quay sẵn** làm nguồn vào. Mục đích của giao diện là minh họa chuỗi:

```text
video TOP -> YOLOv8n TOP -> ByteTrack -> quỹ đạo -> định lượng chuyển động 5 giây -> giao diện
```

Demo chạy hoàn toàn trên CPU Raspberry Pi 4, không dùng Google Coral, EdgeTPU hay `tflite-runtime`. Demo cũng không dùng Random Forest và không nhận dạng bốn lớp hành vi của CAMERA FRONT. Chương trình không sửa `pi_front/`, không ghi đè kết quả nghiên cứu và không tự lưu video/model/output.

## Giới hạn diễn giải khoa học

- `Track ID` chỉ là mã theo dõi cục bộ của ByteTrack, không phải danh tính sinh học cố định.
- “Đối tượng đang theo dõi” là số track đang hoạt động trên lần detector gần nhất, không phải một phép đếm số cá có ground truth.
- Tốc độ được chuẩn hóa theo đường chéo khung hình và có đơn vị `diag/s`, không phải `cm/s`.
- Hiệu quả đường đi nằm trong khoảng 0–1; đổi hướng là thay đổi hướng trung bình tuyệt đối theo radian.
- Không có calibration hình học hoặc vật lý. Các đại lượng chỉ mô tả chuyển động tương đối trong khung hình.
- Chỉ số được tính khi segment hiện tại đã cung cấp đủ cửa sổ 5 giây; trước đó panel hiển thị “Đang thu dữ liệu...”.
- Timestamp của video được lấy từ source timestamp do OpenCV cung cấp, với `frame_index / source_fps` làm fallback đơn điệu. Vì vậy phép tính tốc độ không phụ thuộc chương trình đang chạy nhanh hay chậm.

Nguyên tắc làm sạch bám theo cấu hình nghiên cứu TOP:

- chỉ nội suy gap tối đa 3 source frames;
- median smoothing cửa sổ 5 frame;
- gap dài tạo segment mới;
- không ghép track khác ID;
- feature dùng cửa sổ 5 giây và cập nhật mỗi 1 giây.

## Artifact chuẩn và checksum

Detector nghiên cứu chuẩn:

```text
runs/top/yolov8n_top_v2_baseline/weights/best.pt
SHA-256: 216174c3a40d57bfd7b0d7e46eec90974ddb0b27c879dd1961543e3233a6c5e5
```

Tracker chuẩn:

```text
configs/trackers/top_bytetrack_b15.yaml
```

`runs/`, `*.pt`, `data/raw/` và `*.mp4` bị Git ignore theo chủ đích. Sau khi clone repository trên Raspberry Pi, hãy tự copy model đã lưu trữ vào máy. Ví dụ, có thể đặt model cục bộ tại `pi_top/models/top_yolov8n_best.pt`:

```bash
mkdir -p pi_top/models
cp /duong/dan/luu-tru/top_detector_final.pt pi_top/models/top_yolov8n_best.pt
sha256sum pi_top/models/top_yolov8n_best.pt
```

File `.pt` trong vị trí trên vẫn bị `.gitignore`; không dùng `git add -f`. Tương tự, tự copy video vào `data/raw/top/1.mp4` và `data/raw/top/2.mp4`. Không commit model hoặc video.

## Cài đặt trên Raspberry Pi 4

Khuyến nghị Raspberry Pi OS 64-bit và Python 3.11. Cài thư viện hệ thống cho cửa sổ OpenCV và font tiếng Việt, sau đó tạo môi trường riêng:

```bash
sudo apt update
sudo apt install -y libgl1 libglib2.0-0 fonts-dejavu-core python3-venv
python3 -m venv .venv-pi-top
source .venv-pi-top/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r pi_top/requirements_pi.txt
```

Kiểm tra CLI:

```bash
python3 pi_top/fish_monitor.py --help
```

`ultralytics==8.4.120` được giữ để khớp phiên bản nghiên cứu. Backend mặc định và bắt buộc phải hoạt động trước là `best.pt`. Nếu đã có sẵn một thư mục model NCNN tương thích với Ultralytics, có thể truyền đường dẫn thư mục đó cho `--det-model`; checkpoint này không thực hiện export NCNN.

## Lệnh chạy khuyến nghị

Video 1, detector chạy trên mọi source frame:

```bash
python3 pi_top/fish_monitor.py \
  --source data/raw/top/1.mp4 \
  --det-model runs/top/yolov8n_top_v2_baseline/weights/best.pt \
  --tracker configs/trackers/top_bytetrack_b15.yaml \
  --imgsz 320 \
  --fullscreen \
  --loop-video
```

Video 2, detector chạy mỗi hai source frames:

```bash
python3 pi_top/fish_monitor.py \
  --source data/raw/top/2.mp4 \
  --det-model runs/top/yolov8n_top_v2_baseline/weights/best.pt \
  --tracker configs/trackers/top_bytetrack_b15.yaml \
  --imgsz 320 \
  --detect-every 2 \
  --fullscreen \
  --loop-video
```

Nếu model đã được localize vào `pi_top/models/`, thay đối số model bằng:

```bash
--det-model pi_top/models/top_yolov8n_best.pt
```

Mặc định `--conf 0.50` là detection floor dùng trong tracking TOP để ByteTrack nhận cả dải low/high; ngưỡng high và new-track vẫn là `0.68` trong YAML B15. `--iou` mặc định là `0.70`. Chương trình chỉ xử lý class cá (class ID 0), đặt `--max-det 20`, không dùng built-in plotting và không tạo label/crop.

## Thử cấu hình CPU

So sánh kích thước suy luận 320 và 416:

```bash
python3 pi_top/fish_monitor.py --source data/raw/top/1.mp4 --imgsz 320
python3 pi_top/fish_monitor.py --source data/raw/top/1.mp4 --imgsz 416
```

So sánh detector mỗi frame và mỗi hai frame:

```bash
python3 pi_top/fish_monitor.py --source data/raw/top/1.mp4 --detect-every 1
python3 pi_top/fish_monitor.py --source data/raw/top/1.mp4 --detect-every 2
```

`--detect-every 2` có thể giúp giao diện mượt hơn trên CPU yếu, nhưng detector và ByteTrack chỉ thật sự được gọi ở mỗi frame thứ hai. Box/track gần nhất chỉ được giữ để hiển thị ở frame bị skip; chương trình không tạo observation khoa học giả. Feature chỉ dùng observation thật và nội suy gap tối đa 3 source frames đúng quy tắc TOP. Panel luôn hiển thị `Detection stride` hiện hành.

Khi stride lớn hơn 1, một bước thời gian nội bộ của ByteTrack tương ứng với một lần gọi detector, không phải một source frame. `track_buffer: 15` vẫn được giữ nguyên từ cấu hình B15; không được diễn giải kết quả stride lớn hơn 1 như thể tracker đã cập nhật ở mọi frame.

Video gốc không bị resize vĩnh viễn. YOLO suy luận ở `--imgsz`; bbox, tâm bbox và trajectory được vẽ trong hệ tọa độ video gốc, sau đó toàn bộ vùng video chỉ được resize một lần để đưa vào giao diện.

## Phím điều khiển

- `q` hoặc `ESC`: thoát.
- `SPACE`: pause/resume.
- `r`: reset sạch ByteTrack và history tại vị trí video hiện tại.
- `f`: bật/tắt fullscreen.
- `1`, `2`, `3`: đổi runtime `detect-every` tương ứng.

Khi `--loop-video` quay lại đầu video, ByteTrack, Track ID, segment, feature history và trajectory tail đều được reset; quỹ đạo cuối video không nối với đầu video.

## Benchmark triển khai CPU

Benchmark chạy headless đến cuối một video, không fullscreen và không render panel/video:

```bash
python3 pi_top/fish_monitor.py \
  --source data/raw/top/1.mp4 \
  --det-model runs/top/yolov8n_top_v2_baseline/weights/best.pt \
  --tracker configs/trackers/top_bytetrack_b15.yaml \
  --imgsz 320 \
  --detect-every 1 \
  --benchmark
```

Cuối chương trình sẽ in source FPS, số frame đã đọc, số lần gọi detector, mean/median inference ms, detector FPS và overall pipeline FPS. Đây chỉ là benchmark triển khai CPU; không nhập các số này vào kết quả nghiên cứu cũ.

`--no-panel` có thể dùng trong chế độ cửa sổ để chỉ hiển thị video; trong `--benchmark`, toàn bộ render đã được tắt tự động.

## Gợi ý trình diễn

1. Chạy thử `1.mp4` với `--imgsz 320 --detect-every 1`.
2. Nếu FPS trên Raspberry Pi 4 chưa đủ, giữ video gốc và thử `--detect-every 2` trước; sau đó mới cân nhắc `--imgsz 416` nếu cần đánh đổi tốc độ lấy kích thước suy luận lớn hơn.
3. Xác nhận panel ghi “Đối tượng đang theo dõi”, không diễn giải Track ID thành danh tính sinh học.
4. Dùng `--loop-video` cho phần trình diễn liên tục và bấm `r` nếu muốn bắt đầu lại tracker/history giữa buổi demo.
