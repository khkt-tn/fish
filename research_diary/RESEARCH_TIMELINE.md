# Dòng thời gian nghiên cứu

Timeline này ưu tiên hoạt động khoa học và chỉ dùng ngày đã có evidence. Mốc do yêu cầu phiên cung cấp nhưng chưa tìm thấy trong Git/log/data được giữ dưới dạng `TO_VERIFY`, không biến thành sự kiện đã xác minh.

| Ngày | Hoạt động nghiên cứu | Mức xác minh | Nguồn |
| --- | --- | --- | --- |
| TO_VERIFY (mốc tham khảo 30/07/2026) | Thiết lập Raspberry Pi, camera, collector và thử đồng bộ Drive bằng rclone | TO_VERIFY | Không tìm thấy `collector.log`, `Fish_Front_AI_dataset` hoặc log rclone trong repository hiện tại |
| TO_VERIFY (mốc tham khảo 31/07/2026) | Thiết kế đồng bộ camera và môi trường | TO_VERIFY | Chưa có artifact mang ngày này |
| TO_VERIFY (mốc tham khảo 02/08/2026) | Thu TOP/FRONT, T1/T2 và chuẩn bị Roboflow | TO_VERIFY | Raw hiện có nhưng chưa có metadata chứng minh mốc 02/08 |
| 12/08/2026 | Ghi hai phiên TOP ở bể T2, scenario `baseline`, kèm sensor đầu/cuối | VERIFIED | `data/raw/sensors/1.json`, `data/raw/sensors/2.json` |
| TO_VERIFY (mốc tham khảo 10/08/2026) | Validation detector | TO_VERIFY | Git evidence sớm nhất của validation là 17/08/2026 |
| 14/08/2026 | Export Roboflow Front version 1, 1.269 ảnh | VERIFIED | Metadata local `data/roboflow/front_detect_v1/README.roboflow.txt` |
| TO_VERIFY (mốc tham khảo 14/08/2026) | Raspberry Pi + Coral, tracker, behavior và quan sát khoảng 3 FPS | TO_VERIFY | Không tìm thấy benchmark/log phần cứng hoặc số 3 FPS |
| 17/08/2026 | Audit dataset Front, train/evaluate YOLOv8n, visibility audit, ByteTrack ablation và tracker benchmark | VERIFIED | Các checkpoint Git từ `b3b6d2f` đến `b0407b7` |
| 19/08/2026 | Hoàn thiện đặc trưng/nhãn/mô hình hành vi Front và code demo Coral | VERIFIED cho artifact; PARTIAL cho chạy phần cứng | Commit `622a94b` |
| 29/08/2026 | Hoàn thiện detection/tracking TOP | VERIFIED | Commit `4c582fc` |
| 29/08/2026 | Hoàn thiện đặc trưng hành vi TOP | VERIFIED | Commit `cc74ce9` |
| 29/08/2026 | Ghép metadata môi trường cấp phiên và phân tích mô tả hành vi | VERIFIED | Commit `dbc51a9` |
| 30/08–10/09/2026 | Audit khả năng tái lập | PLANNED | [J11](entries/J11_reproducibility_audit.md) |
| 11/09–17/09/2026 | Kiểm chứng thống kê và độ tin cậy | PLANNED | [J12](entries/J12_statistical_validation.md) |
| 18/09–01/10/2026 | Hoàn thiện báo cáo khoa học | PLANNED | [J13](entries/J13_scientific_report.md) |
| TO_VERIFY | Xây dựng poster và video demo | PLANNED | [J14](entries/J14_poster_and_demo.md) |
| 13/10–16/10/2026 | Chuẩn bị phản biện | PLANNED | [J15](entries/J15_defense_preparation.md) |
| 20/10/2026 | Khóa và lưu trữ dự án | PLANNED | [J16](entries/J16_final_project_archive.md) |

## Ghi chú về ngày

Git history hiện tại bắt đầu ngày 17/08/2026. Vì vậy, ngày 12/08 và 14/08 ở trên đến từ metadata dữ liệu nguồn; các mốc tháng 7/đầu tháng 8 khác cần học sinh cung cấp ảnh, log hoặc lịch sử từ thiết bị gốc.
