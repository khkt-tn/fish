# Nhật ký nghiên cứu Fish AI

**Đề tài:** Phân tích hành vi cá cảnh sử dụng trí tuệ nhân tạo từ dữ liệu hình ảnh và môi trường

**Học sinh thực hiện:**

- Phạm Duy Quang Anh — K37 Toán, THPT Chuyên Thái Nguyên
- Nguyễn Quốc Minh — K37 Toán, THPT Chuyên Thái Nguyên

## Mục đích

Thư mục này là nhật ký nghiên cứu dạng Markdown để đọc trực tiếp trên GitHub. Nội dung ghi lại câu hỏi, phương pháp, quan sát, sai sót, điều chỉnh và bằng chứng của dự án đến ngày mốc **29/08/2026** theo múi giờ **Asia/Bangkok (+07:00)**. Nhật ký không thay thế dữ liệu thô, notebook hay log thực nghiệm.

## Quy ước trạng thái

- `VERIFIED`: có bằng chứng trực tiếp trong repository, log hoặc dữ liệu hiện có.
- `PARTIAL`: công việc hoặc artifact đã có nhưng bằng chứng chưa đủ để xác nhận toàn bộ câu chuyện.
- `TO_VERIFY`: cần học sinh bổ sung hoặc xác nhận; không được coi là kết quả đã chứng minh.
- `PLANNED`: công việc chưa thực hiện tại ngày 29/08/2026.

## Tình trạng tổng quát

| Nhóm | Số bài |
| --- | ---: |
| VERIFIED | 8 |
| PARTIAL | 1 |
| TO_VERIFY | 0 |
| PLANNED | 4 |
| Tổng | 13 |

Bài `PARTIAL` liên quan đến triển khai Raspberry Pi/Coral: repository có mô tả hoặc code nhưng thiếu log phần cứng, benchmark hay bằng chứng lịch sử được yêu cầu.

## Danh mục bài

| ID | Nội dung | Trạng thái | Experiment |
| --- | --- | --- | --- |
| [J01](entries/J01_data_acquisition.md) | Xây dựng hệ thống thu nhận và lưu trữ dữ liệu | VERIFIED | EXP-01 |
| [J02](entries/J02_top_front_data_collection.md) | Thu thập dữ liệu từ camera TOP và FRONT | VERIFIED | EXP-02 |
| [J03](entries/J03_roboflow_dataset.md) | Xây dựng bộ dữ liệu gán nhãn trên Roboflow | VERIFIED | EXP-03 |
| [J04](entries/J04_yolo_detection.md) | Huấn luyện và đánh giá mô hình phát hiện cá | VERIFIED | EXP-04 |
| [J05](entries/J05_fish_tracking.md) | Theo dõi từng cá thể bằng ByteTrack | VERIFIED | EXP-05 |
| [J06](entries/J06_behavior_features.md) | Xây dựng đặc trưng hành vi cá | VERIFIED | EXP-05 |
| [J07](entries/J07_raspberry_pi_coral.md) | Chuẩn bị pipeline Raspberry Pi và Coral Edge TPU | PARTIAL | EXP-06 |
| [J08](entries/J08_sensor_behavior_sync.md) | Đồng bộ đặc trưng hành vi với dữ liệu môi trường | VERIFIED | EXP-07 |
| [J09](entries/J09_environment_behavior_analysis.md) | Phân tích mối liên hệ giữa môi trường và hành vi | VERIFIED | EXP-08 |
| [J10](entries/J10_scientific_report.md) | Hoàn thiện báo cáo khoa học | PLANNED | EXP-11 |
| [J11](entries/J11_poster_and_demo.md) | Xây dựng poster và video demo | PLANNED | EXP-12 |
| [J12](entries/J12_defense_preparation.md) | Chuẩn bị phản biện | PLANNED | EXP-13 |
| [J13](entries/J13_final_project_archive.md) | Khóa dự án và lưu trữ bằng chứng | PLANNED | EXP-14 |

## Điều hướng

- [Giới thiệu dự án](ABOUT_PROJECT.md)
- [Dòng thời gian nghiên cứu](RESEARCH_TIMELINE.md)
- [Chỉ mục minh chứng](EVIDENCE_INDEX.md)
- [Chỉ mục ảnh và video](MEDIA_INDEX.md)
- [Nhật ký đóng góp](CONTRIBUTION_LOG.md)
- [Báo cáo phiên xây dựng nhật ký](CODEX_SESSION_REPORT.md)

