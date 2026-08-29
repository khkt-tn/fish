---
journal_id: J11
experiment_id: EXP-09
title: "Kiểm tra khả năng tái lập kết quả"
date: "2026-08-30"
status: PLANNED
authors:
  - "Phạm Duy Quang Anh"
  - "Nguyễn Quốc Minh"
tags:
  - reproducibility
  - audit
  - provenance
evidence_level: pending
last_updated: "2026-08-29"
---

# Kiểm tra khả năng tái lập kết quả

## 1. Mục tiêu

Kiểm tra liệu các checkpoint chính có thể được tái tạo từ input đã khóa, config, notebook, environment và model đúng phiên bản hay không.

## 2. Vấn đề cần giải quyết

Kết quả hiện có trải qua nhiều notebook và một phần input nằm ngoài Git. Nếu checksum, version hoặc thứ tự chạy không rõ, một lần chạy lại có thể dùng nhầm dataset/model và tạo kết quả tưởng là tái lập.

## 3. Thiết bị, dữ liệu và phần mềm

Dự kiến dùng Conda `fish`, notebook trong repository, dataset version đã ghi, raw working copy do user chuẩn bị thủ công và model kiểm tra bằng SHA-256. Không tự login Drive/Roboflow.

## 4. Phương pháp thực hiện

Audit từng checkpoint theo chuỗi input → config → code → log → result. So sánh checksum, row count, schema và metric trong tolerance được định nghĩa trước; không sửa nhiều biến cùng lúc.

## 5. Quá trình thực hiện

Kế hoạch 30/08–10/09/2026:

- [ ] Chọn checkpoint và ghi phạm vi.
- [ ] Xác nhận kernel `fish`, Python, package, GPU.
- [ ] Kiểm tra input tồn tại và checksum.
- [ ] Kiểm tra dataset/version và split metadata.
- [ ] Kiểm tra config, random seed và model hash.
- [ ] User chạy notebook thủ công trong VS Code theo đúng thứ tự.
- [ ] So sánh output mới với evidence đã commit.
- [ ] Ghi mọi sai lệch và nguyên nhân có thể.

## 6. Kết quả và quan sát

`PLANNED`: chưa có rerun hoặc metric tái lập mới tại ngày 29/08/2026.

## 7. Vấn đề phát sinh

Notebook 09 có HOTA chưa được tính và output tương tác chứa các `ValueError` do frame ngoài phạm vi; audit cần phân biệt lịch sử thao tác GUI với lỗi pipeline. Input nặng có thể không còn trên máy khác.

## 8. Điều chỉnh và cải tiến

Nếu sai lệch xảy ra, chỉ thay đổi nguyên nhân nhỏ nhất, giữ output cũ và tạo experiment ID mới. Không ghi đè baseline hoặc nâng cấp package hàng loạt.

## 9. Kết luận tại thời điểm thực hiện

Chưa có kết luận. Một checkpoint chỉ được đánh dấu tái lập khi input, config, environment và metric đều có evidence đối chiếu.

## 10. Minh chứng

- [Git evidence](../evidence/github_evidence.md)
- [Unresolved items](../evidence/unresolved.md)
- [`environment/environment.yml`](../../environment/environment.yml)

## 11. Hình ảnh đề xuất

<!-- TODO_MEDIA:
source: future reproducibility comparison table
timestamp: N/A
description: Bảng baseline so với rerun và sai lệch metric
-->

## 12. Video minh họa

Không bắt buộc; ưu tiên bảng và log tái lập. Nếu quay, dùng `TODO_YOUTUBE_VIDEO_ID`.

## 13. Đóng góp của thành viên

`TO_VERIFY_WITH_STUDENTS` sau mỗi checkpoint audit.

## 14. Công việc tiếp theo

Chỉ chuyển sang J12 sau khi user xác nhận phạm vi audit đã pass và evidence mới được lưu đúng chỗ.
