---
journal_id: J08
experiment_id: EXP-06
title: "Tối ưu tốc độ xử lý thời gian thực"
date: "2026-08-19"
status: PARTIAL
authors:
  - "Phạm Duy Quang Anh"
  - "Nguyễn Quốc Minh"
tags:
  - realtime
  - optimization
  - benchmark
evidence_level: low
last_updated: "2026-08-29"
---

# Tối ưu tốc độ xử lý thời gian thực

## 1. Mục tiêu

Tìm cấu hình giảm độ trễ nhưng vẫn giữ detection/tracking đủ ổn định cho quan sát hành vi trên thiết bị biên.

## 2. Vấn đề cần giải quyết

Preprocess, detector, tracker, feature, vẽ overlay, display và logging đều tiêu tốn thời gian. Giảm độ phân giải có thể tăng tốc nhưng cũng làm cá nhỏ khó phát hiện.

## 3. Thiết bị, dữ liệu và phần mềm

Code demo hỗ trợ `--imgsz`, camera width/height/FPS và display 800×480. Hướng dẫn đề xuất export 512 trước và so 320 với 512 trên cùng video. Chưa có file benchmark Raspberry Pi.

## 4. Phương pháp thực hiện

Phương án đúng về khoa học là giữ cùng video, model format và pipeline, chỉ thay một biến như `imgsz`; đo inference ms, pipeline FPS, detection/tracking diagnostic và nhiệt độ. Bounding box được Ultralytics trả về theo frame dùng cho pipeline; display có resize riêng cho giao diện.

## 5. Quá trình thực hiện

Repository chứng minh hướng tối ưu đã được thiết kế trong code và tài liệu. Mốc “khoảng 3 FPS”, việc quay lại bản live ổn định hoặc sửa camera index không có log, nên được giữ như nội dung cần người dùng xác minh.

## 6. Kết quả và quan sát

Chưa có FPS trước/sau đủ bằng chứng. Không tự điền FPS cuối, không coi 512 là cấu hình tối ưu và không tuyên bố 320 đã được benchmark.

## 7. Vấn đề phát sinh

Thiếu telemetry theo stage khiến chưa biết bottleneck nằm ở detector, tracker, display hay I/O. Chỉ nhìn video giật không cho phép so sánh định lượng.

## 8. Điều chỉnh và cải tiến

Kế hoạch benchmark cần tách thời gian detector khỏi toàn pipeline, dùng warm-up, cùng độ dài clip và ít nhất vài lần lặp. Nếu một tối ưu làm mất prediction, phải ghi cả chất lượng lẫn tốc độ trước khi quay lại cấu hình ổn định.

## 9. Kết luận tại thời điểm thực hiện

Hướng tối ưu hóa đã được chuẩn bị nhưng kết quả runtime chưa được xác minh. Bài ở trạng thái `PARTIAL`, không phải một thí nghiệm hiệu năng hoàn chỉnh.

## 10. Minh chứng

- [`README_PI_FRONT_DEMO.md`](../../pi_front/README_PI_FRONT_DEMO.md)
- [`fish_monitor.py`](../../pi_front/fish_monitor.py)
- [Unresolved evidence](../evidence/unresolved.md)

## 11. Hình ảnh đề xuất

<!-- TODO_MEDIA:
source: future Pi benchmark capture
timestamp: N/A
description: IMG-J08-01 FPS trước; IMG-J08-02 config resolution; IMG-J08-03 FPS sau
-->

## 12. Video minh họa

> 🎥 **V09 — So sánh pipeline trước và sau tối ưu**
>
> YouTube: `TODO_YOUTUBE_VIDEO_ID`

Ưu tiên split-screen cùng timestamp sau khi có benchmark thật.

## 13. Đóng góp của thành viên

`TO_VERIFY_WITH_STUDENTS`: chưa có evidence phân công profiling, tối ưu hoặc quay demo.

## 14. Công việc tiếp theo

Thực hiện benchmark có kiểm soát trong Notebook 18 khi được phê duyệt; lưu bảng nhỏ vào `results/` và không dùng một quan sát duy nhất làm kết luận.
