# Chỉ mục ảnh và video

Không file video nào được đưa vào commit. Đường dẫn local dưới đây chỉ là gợi ý nguồn để người dùng biên tập và upload.

| ID | Loại | Nội dung | Bài sử dụng | Trạng thái | URL/File |
| --- | --- | --- | --- | --- | --- |
| V01 | Video | Raspberry Pi + camera acquisition | J01 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; source cần xác nhận |
| V02 | Video | TOP raw video | J02 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; gợi ý `data/raw/top/1.mp4` |
| V03 | Video | FRONT raw video | J02 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; gợi ý `data/raw/front/3.mp4` |
| V04 | Video | Roboflow annotation | J03 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; cần quay màn hình thủ công |
| V05 | Video | YOLO detection | J04 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; gợi ý `outputs/front/detection/conf068_n1/front_detection_overlay.mp4` |
| V06 | Video | ByteTrack tracking | J05 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; chọn overlay local sau khi kiểm tra |
| V07 | Video | Behavior overlay | J06 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; nguồn local cần xác nhận |
| V08 | Video | Pi + Coral live inference | J07 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; chưa có evidence runtime trong repository |
| V10 | Video | Hành vi + môi trường đồng bộ | J08 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; cần dựng từ session mapping đã xác nhận |
| V11 | Video | Pipeline đầy đủ tới phân tích môi trường | J09 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; đề xuất 2–4 phút |
| V12 | Video | Demo cuối dự án | J11 | TODO_UPLOAD | `TODO_YOUTUBE_URL`; PLANNED |

## Template YouTube

```md
[![Xem video](https://img.youtube.com/vi/YOUTUBE_VIDEO_ID/maxresdefault.jpg)](https://youtu.be/YOUTUBE_VIDEO_ID)
```

## Quy tắc ảnh

- Ưu tiên plot nhỏ đã theo dõi bằng Git trong `results/`.
- Không copy hàng loạt frame hoặc video vào nhật ký.
- Với ảnh chưa có, giữ comment `TODO_MEDIA` gồm source, timestamp và mô tả.
