# Các mục chưa giải quyết

## Evidence lịch sử

- Không tìm thấy `collector.log`, `Fish_Front_AI_dataset` hoặc log rclone.
- Chưa xác minh mốc 30/07, 31/07, 02/08 và 10/08/2026.
- Chưa xác minh ngày thu các raw video Front hoặc ý nghĩa chính xác của T1/T2.

## Raspberry Pi và Coral

- Có code demo và file `*_edgetpu.tflite` local bị ignore.
- Chưa có log xác nhận chạy trên Raspberry Pi/Coral thật.
- Chưa có evidence cho quan sát khoảng 3 FPS.
- Chưa có benchmark 320 so với 512, before/after FPS, latency, CPU, RAM hoặc nhiệt độ.
- Vấn đề chọn sai camera index chưa có log trong repository.

## Metric và tái lập

- HOTA là `null` trong summary MOT hiện tại.
- Ba segment MOT bị skip vì identity uncertain; chỉ một segment có official status `OK`.
- Notebook 09 có các `ValueError` được lưu trong output của GUI do yêu cầu frame ngoài phạm vi; cần xác nhận đây chỉ là lịch sử thao tác tương tác trước audit tái lập.
- Notebook 18 benchmark Raspberry Pi và Notebook 19 tổng hợp cuối chưa tồn tại tại ngày mốc.

## Media và đóng góp

- V01–V12 đều chưa có YouTube URL.
- Ảnh setup Raspberry Pi, Roboflow annotation và màn hình live chưa có bản commit nhỏ phù hợp.
- Mọi phân công cá nhân cần `TO_VERIFY_WITH_STUDENTS`.
