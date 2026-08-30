---
journal_id: J05
experiment_id: EXP-05
title: "Theo dõi từng cá thể bằng ByteTrack"
date: "2026-08-17"
status: VERIFIED
authors:
  - "Phạm Duy Quang Anh"
  - "Nguyễn Quốc Minh"
tags:
  - tracking
  - bytetrack
  - trajectory
evidence_level: high
last_updated: "2026-08-29"
---

# Theo dõi từng cá thể bằng ByteTrack

## 1. Mục tiêu

Nối detection giữa các frame thành track đủ liên tục để tính trajectory và đặc trưng hành vi.

## 2. Vấn đề cần giải quyết

Cá giao nhau, che khuất, đi vào nơi không nhìn thấy hoặc bị detector bỏ sót có thể làm tracker mất track, phân mảnh trajectory hoặc đổi ID. Overlay nhiều ID không tự chứng minh tracking đúng.

## 3. Thiết bị, dữ liệu và phần mềm

Front dùng cùng model SHA-256 `750b0f...7738`, video checksum cố định và các YAML ByteTrack B15/B30/B60. TOP sau đó dùng ByteTrack B15 riêng cho hai video TOP.

## 4. Phương pháp thực hiện

Ablation chỉ thay `track_buffer` 15, 30, 60 trong khi giữ threshold. Benchmark Front so ByteTrack B15 với BoT-SORT. Diagnostic gồm coverage khi cá visible, fragment, gap, lifespan, ID count và processing FPS.

## 5. Quá trình thực hiện

Trên video Front một cá, cả B15/B30/B60 có quality diagnostic gần như giống nhau; B15 được chọn tạm thời vì buffer nhỏ nhất khi hòa. Benchmark sau đó cho thấy ByteTrack và BoT-SORT có coverage giống nhau trong bài kiểm tra này, ByteTrack chạy nhanh hơn.

## 6. Kết quả và quan sát

B15 có visible track coverage 0,999143, 2 frame visible không có track, 1 excess fragment và processing khoảng 52,41 FPS trong ablation. Tuy nhiên đây là video một cá. TOP tracking về sau có 33 và 53 unique IDs, nhiều track ngắn và gap, cho thấy identity fragmentation rõ trong bài toán nhiều cá.

## 7. Kết luận tại thời điểm thực hiện

ByteTrack đã tạo trajectory phục vụ bước đặc trưng, nhưng `track_id` không phải danh tính sinh học. B15 là lựa chọn kỹ thuật tạm thời chứ không phải bằng chứng ByteTrack tối ưu cho mọi video nhiều cá.

## 8. Minh chứng

- [`front_bytetrack_ablation.csv`](../../results/tracking/front_bytetrack_ablation.csv)
- [`front_tracker_benchmark.csv`](../../results/tracking/front_tracker_benchmark.csv)
- [`front_mot_official_metrics_by_segment.csv`](../../results/tracking/front_mot_official_metrics_by_segment.csv)
- [`top_bytetrack_baseline_summary.csv`](../../results/tracking/top_bytetrack_baseline_summary.csv)
- Commits `78ed4c1`, `b0407b7`, `4c582fc`

## 9. Video minh họa

<div class="video-container">
  <iframe
    src="https://www.youtube.com/embed/rPQRHIZd1WI"
    title="V03 — Video raw camera FRONT"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen>
  </iframe>
</div>

## 10. Đóng góp của thành viên

Quang Anh - Quốc Minh

