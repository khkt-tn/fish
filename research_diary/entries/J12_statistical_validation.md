---
journal_id: J12
experiment_id: EXP-10
title: "Kiểm chứng thống kê và độ tin cậy"
date: "2026-09-11"
status: PLANNED
authors:
  - "Phạm Duy Quang Anh"
  - "Nguyễn Quốc Minh"
tags:
  - statistics
  - uncertainty
  - validation
evidence_level: pending
last_updated: "2026-08-29"
---

# Kiểm chứng thống kê và độ tin cậy

## 1. Mục tiêu

Đánh giá độ tin cậy của feature và so sánh hành vi bằng phương pháp phù hợp với thiết kế thí nghiệm và cỡ mẫu thật.

## 2. Vấn đề cần giải quyết

Window chồng lấp không phải replicate độc lập; hiện chỉ có hai phiên môi trường. Nếu coi hàng trăm window là hàng trăm mẫu độc lập, độ chắc chắn sẽ bị phóng đại.

## 3. Thiết bị, dữ liệu và phần mềm

Dự kiến dùng các bảng nhỏ trong `results/`, metadata session, schema feature và một protocol thống kê được viết trước khi xem kết quả mới.

## 4. Phương pháp thực hiện

- [ ] Mô tả phân phối, missing data và outlier.
- [ ] Xác định đơn vị lặp độc lập: session, video, cá thể hay window.
- [ ] Chọn correlation chỉ khi có đủ cặp quan sát độc lập.
- [ ] Báo effect size và confidence interval khi phù hợp.
- [ ] Thực hiện sensitivity analysis theo tracking coverage/fragmentation.
- [ ] Ghi rõ giới hạn cỡ mẫu và multiple comparison.
- [ ] Không diễn giải correlation thành causation.

## 5. Quá trình thực hiện

Khoảng dự kiến 11/09–17/09/2026. Trước khi chạy, nhóm cần quyết định có thu thêm phiên lặp hay giới hạn bài ở descriptive analysis.

## 6. Kết quả và quan sát

`PLANNED`: chưa có p-value, effect size, interval hoặc sensitivity result được xác minh.

## 7. Vấn đề phát sinh

Temperature và pH hiện không biến thiên, còn light bị confound với session. Thiết kế hiện tại không thể trả lời causal question chỉ bằng một kỹ thuật thống kê khác.

## 8. Điều chỉnh và cải tiến

Nếu chưa đủ replicate, kết quả hợp lệ là nêu `NOT_TESTABLE` hoặc giữ phân tích mô tả, thay vì ép tính significance. Thu thêm dữ liệu phải theo protocol xác định trước.

## 9. Kết luận tại thời điểm thực hiện

Chưa có kết luận thống kê. Phương pháp sẽ được chọn dựa trên đơn vị lặp và thiết kế, không dựa trên mong muốn có kết quả có ý nghĩa.

## 10. Minh chứng

- [`environment_behavior_comparison.csv`](../../results/environment/environment_behavior_comparison.csv)
- [`TOP_ENV_BEHAVIOR_001/summary.json`](../../logs/environment/TOP_ENV_BEHAVIOR_001/summary.json)

## 11. Hình ảnh đề xuất

<!-- TODO_MEDIA:
source: future statistical outputs
timestamp: N/A
description: Distribution, effect-size plot và sensitivity summary nếu phương pháp hợp lệ
-->

## 12. Video minh họa

Không ưu tiên video; dùng plot và bảng. YouTube nếu cần: `TODO_YOUTUBE_VIDEO_ID`.

## 13. Đóng góp của thành viên

`TO_VERIFY_WITH_STUDENTS`: xác nhận người thiết kế protocol, kiểm tra giả định và diễn giải.

## 14. Công việc tiếp theo

Khóa quyết định thống kê và limitation trước khi tổng hợp báo cáo J13.
