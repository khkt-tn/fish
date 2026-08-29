---
journal_id: J13
experiment_id: EXP-11
title: "Hoàn thiện báo cáo khoa học"
date: "2026-09-18"
status: PLANNED
authors:
  - "Phạm Duy Quang Anh"
  - "Nguyễn Quốc Minh"
tags:
  - scientific-report
  - writing
  - provenance
evidence_level: pending
last_updated: "2026-08-29"
---

# Hoàn thiện báo cáo khoa học

## 1. Mục tiêu

Tổng hợp câu hỏi, phương pháp, kết quả, giới hạn và đóng góp thành một báo cáo khoa học có thể truy ngược từng con số tới evidence.

## 2. Vấn đề cần giải quyết

Báo cáo phải tách detection, tracking, behavior, environment và deployment; tránh dùng một metric ở sai ngữ cảnh hoặc lặp lại câu chuyện kỹ thuật như changelog.

## 3. Thiết bị, dữ liệu và phần mềm

Nguồn viết gồm nhật ký J01–J12, notebook, `results/`, `logs/`, figure đã commit và tài liệu tham khảo được kiểm tra. Không đưa raw video hoặc model binary vào báo cáo Git.

## 4. Phương pháp thực hiện

Khung dự kiến:

1. Đặt vấn đề: lý do, thực trạng, khoảng trống, câu hỏi, mục tiêu, phạm vi.
2. Cơ sở khoa học và công nghệ: hành vi cá, môi trường, cảm biến, detection/tracking, feature và hệ thống nhúng.
3. Vật liệu và phương pháp: thiết kế dữ liệu, annotation, model, metric, đồng bộ và thống kê.
4. Kết quả: detection, tracking, feature, environment và deployment theo evidence.
5. Thảo luận: ý nghĩa, sai số, giới hạn, khả năng khái quát.
6. Kết luận và hướng phát triển.

## 5. Quá trình thực hiện

Khoảng dự kiến 18/09–01/10/2026. Mỗi bảng/figure được gắn experiment ID, nguồn và caption nêu đúng mức kết luận.

## 6. Kết quả và quan sát

`PLANNED`: nhật ký này chưa viết thay báo cáo và chưa tạo kết luận cuối dự án.

## 7. Vấn đề phát sinh

Các phần J01, J07, J08 còn `PARTIAL`; contribution chưa xác minh; deployment benchmark và một số metric MOT còn thiếu. Báo cáo không được che các khoảng trống này.

## 8. Điều chỉnh và cải tiến

Dùng bảng provenance để kiểm tra mỗi con số. Thuật ngữ “accuracy”, “identity”, “stress” và “cause” chỉ dùng khi evidence tương ứng cho phép.

## 9. Kết luận tại thời điểm thực hiện

Chưa có báo cáo hoàn chỉnh tại ngày mốc. Bộ nhật ký là khung evidence để giảm sai lệch khi viết.

## 10. Minh chứng

- [README nhật ký](../README.md)
- [Evidence index](../EVIDENCE_INDEX.md)
- [Research timeline](../RESEARCH_TIMELINE.md)

## 11. Hình ảnh đề xuất

<!-- TODO_MEDIA:
source: selected committed results plots
timestamp: N/A
description: Sơ đồ pipeline, dataset sample, detection, tracking, behavior và environment plots có caption
-->

## 12. Video minh họa

Không bắt buộc trong báo cáo; tham chiếu V11/V12 khi URL đã xác nhận.

## 13. Đóng góp của thành viên

`TO_VERIFY_WITH_STUDENTS`: xác nhận người soạn từng mục, kiểm tra nguồn và biên tập.

## 14. Công việc tiếp theo

Sau review nội dung khoa học, chuyển các kết quả chính sang poster/demo mà không thêm metric mới chưa kiểm chứng.
