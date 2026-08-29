# Giới thiệu dự án

## Câu hỏi nghiên cứu

Dự án tìm cách chuyển dữ liệu hình ảnh cá và dữ liệu môi trường thành các mô tả định lượng có thể truy xuất và kiểm tra. Chuỗi xử lý chính gồm thu hình, xây dựng dataset, phát hiện cá, theo dõi theo thời gian, tạo đặc trưng hành vi và ghép với bối cảnh môi trường.

## Hai góc quan sát

Camera FRONT hỗ trợ quan sát vị trí theo chiều cao, chuyển động theo phương đứng và các vùng gần mặt nước, giữa bể hoặc đáy. Camera TOP hỗ trợ quỹ đạo trên mặt phẳng ảnh, khoảng cách giữa các track, độ phân tán và hướng chuyển động của nhóm.

Hai camera được phát triển độc lập. `track_id` chỉ là định danh của tracker trong một video, không phải danh tính sinh học và không được dùng để giả định rằng một ID FRONT trùng với một ID TOP.

## Dữ liệu và mô hình

- Raw video và sensor là dữ liệu nguồn, được giữ ngoài Git khi nặng.
- Roboflow là nguồn quản lý dataset detection đã gán nhãn.
- YOLOv8n được dùng làm detector nhẹ có khả năng hướng tới thiết bị biên.
- ByteTrack và BoT-SORT đã được kiểm tra trong các bước tracking.
- Đặc trưng hành vi được mô tả bằng đại lượng quan sát được như tốc độ, quãng đường, độ ngoặt, khoảng cách láng giềng và độ phân tán.

## Giới hạn khoa học

Dự án không coi count diagnostic là độ chính xác MOT, không coi `track_id` là danh tính cá vĩnh viễn và không suy ra stress, sức khỏe hay trạng thái cảm xúc khi chưa có ground truth sinh học. Phân tích môi trường hiện tại chỉ gồm hai phiên có sensor đầu/cuối, nên là so sánh mô tả giữa phiên chứ không chứng minh quan hệ nhân quả.

## Chuỗi bằng chứng

```text
kết quả trong bài
↓
results/
↓
experiment_id và logs/
↓
notebook/config
↓
Git commit
↓
dataset, model và dữ liệu nguồn
```

Xem [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md) để tra đường dẫn cụ thể.
