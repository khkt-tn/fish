# Demo CAMERA TOP xử lý trước cho Raspberry Pi 3 B+

Raspberry Pi 3 B+ không đủ nhanh để chạy trực tiếp YOLOv8n `.pt` ở tốc độ phù hợp cho phần trình diễn. Vì vậy demo chính dùng video giao diện đã được render trên máy nghiên cứu từ kết quả AI hiện có. Raspberry Pi chỉ phát video kết quả theo đúng thời gian nguồn bằng `mpv`.

Đây **không phải inference real-time trên Raspberry Pi**. Video nguồn là video thí nghiệm thật của dự án, không phải video mô phỏng.

Pipeline khoa học tạo ra artifact nguồn vẫn là:

```text
video TOP
→ YOLOv8n TOP
→ ByteTrack B15
→ trajectory cleaning
→ behavior features
```

Video giao diện lấy bbox, confidence và Track ID từ raw tracking CSV; lấy trajectory tail từ cleaned trajectory cùng `trajectory_uid`; lấy tốc độ, hiệu quả đường đi và mức đổi hướng từ feature window TOP đã được nghiên cứu tạo ra. Script build không chạy lại YOLO, ByteTrack, training hay model behavior.

## Giới hạn diễn giải khoa học

- Track ID và `trajectory_uid` là mã theo dõi cục bộ, không phải danh tính sinh học.
- “Đối tượng đang theo dõi” là số track có observation ở frame hiện tại, không phải ground-truth số cá.
- Tốc độ có đơn vị `diag/s`, được chuẩn hóa theo đường chéo khung hình; đây không phải `cm/s`.
- Hiệu quả đường đi là net displacement / total path distance, trong khoảng 0–1.
- Đổi hướng là mean absolute turning angle, đơn vị rad.
- Feature dùng cửa sổ 5 giây, bước 1 giây và coverage tối thiểu 0.6. Panel chỉ dùng cửa sổ đã kết thúc tại source timestamp hiện tại; nếu chưa có cửa sổ hợp lệ sẽ ghi “Đang thu dữ liệu...”.
- Trajectory cleaning chỉ nội suy gap tối đa 3 frame, smoothing 5 frame, không stitch qua ID. Tail không nối qua `trajectory_uid` khác.

## Build trên máy nghiên cứu

Kích hoạt Conda environment `fish`, rồi từ repository root chạy:

```bash
cd /home/diy-hus/fish
conda activate fish

python3 pi_top/build_precomputed_demo.py --video-id 1
python3 pi_top/build_precomputed_demo.py --video-id 2
```

Hoặc render cả hai video và tạo gói copy sang Pi:

```bash
python3 pi_top/build_precomputed_demo.py --all
```

Đầu ra local (đã được `.gitignore`):

```text
pi_top/demo/top_demo_1.mp4
pi_top/demo/top_demo_2.mp4
artifacts_local/pi_top_precomputed_demo/
artifacts_local/pi_top_precomputed_demo.tar.gz
```

Hai video cuối có độ phân giải 800×480, H.264/yuv420p, không audio và giữ FPS nguồn. Vùng video bên trái giữ nguyên tỷ lệ; panel tiếng Việt nằm bên phải. Các screenshot và báo cáo QA local nằm tại `artifacts_local/pi_top_precomputed_demo_qa/`.

`pi_top/fish_monitor_cpu_slow.py` giữ lại nguyên bản thử nghiệm CPU cũ. Không dùng file này cho demo xử lý trước.

## Copy sang Raspberry Pi

Copy trực tiếp bốn file cần thiết:

```bash
ssh pi@<PI_IP> 'mkdir -p /home/pi/fish/pi_top/demo'
scp pi_top/demo/top_demo_1.mp4 \
    pi_top/demo/top_demo_2.mp4 \
    pi@<PI_IP>:/home/pi/fish/pi_top/demo/
scp pi_top/fish_monitor.py \
    pi_top/README_PI_TOP_PRECOMPUTED_DEMO.md \
    pi@<PI_IP>:/home/pi/fish/pi_top/
```

Hoặc copy và giải nén `artifacts_local/pi_top_precomputed_demo.tar.gz`.

## Cài đặt và chạy trên Pi

Player không cần pip package, Torch, Ultralytics, OpenCV, ByteTrack, LAP, SciPy, scikit-learn, Coral hay EdgeTPU. Chỉ cài dependency hệ thống:

```bash
sudo apt update
sudo apt install -y mpv
```

Lệnh mặc định phát video 1 ở fullscreen và loop vô hạn:

```bash
cd ~/fish
python3 pi_top/fish_monitor.py
```

Chọn video:

```bash
python3 pi_top/fish_monitor.py --video 1
python3 pi_top/fish_monitor.py --video 2
python3 pi_top/fish_monitor.py --video demo/top_demo_1.mp4
```

Phím do `mpv` cung cấp:

- `SPACE`: pause/resume.
- `f`: bật/tắt fullscreen.
- `q`: thoát.
- `left` / `right`: tua video.

Khi video loop, toàn bộ bbox, quỹ đạo và panel trở lại đầu sạch vì chúng đã được render sẵn theo từng frame.
