---
journal_id: J16
experiment_id: EXP-14
title: "Khóa dự án và lưu trữ bằng chứng"
date: "2026-10-20"
status: PLANNED
authors:
  - "Phạm Duy Quang Anh"
  - "Nguyễn Quốc Minh"
tags:
  - archive
  - release
  - reproducibility
evidence_level: pending
last_updated: "2026-08-29"
---

# Khóa dự án và lưu trữ bằng chứng

## 1. Mục tiêu

Đóng băng phiên bản cuối có thể truy xuất, bảo vệ raw source/model quan trọng và xác nhận repository chứa đủ research evidence.

## 2. Vấn đề cần giải quyết

Dữ liệu nặng nằm ngoài Git, còn model cuối cần backup riêng. Nếu xóa local trước khi kiểm tra Drive/Roboflow/model archive, dự án có thể mất khả năng tái lập.

## 3. Thiết bị, dữ liệu và phần mềm

Git repository, Google Drive raw archive, Roboflow dataset versions, final model archive, checksum manifest, notebook/log/result và bản báo cáo cuối.

## 4. Phương pháp thực hiện

- [ ] Kiểm tra Git status và staged scope.
- [ ] Kiểm tra commit history/checkpoint.
- [ ] Khóa dataset/version và split metadata.
- [ ] Kiểm tra notebook, figure, citation và README.
- [ ] Hoàn thiện Contribution Log.
- [ ] Backup raw data và model cuối, lưu checksum/manifest.
- [ ] Xác nhận không có secret hoặc binary nặng trong Git.
- [ ] Tạo final tag/release nếu phù hợp và được user phê duyệt.

## 5. Quá trình thực hiện

Dự kiến ngày 20/10/2026. Đây là kế hoạch; phiên 29/08 không tạo release hoặc giả lập trạng thái tương lai.

## 6. Kết quả và quan sát

`PLANNED`: chưa có final tag, release hoặc archive confirmation.

## 7. Vấn đề phát sinh

Không được tự động xóa raw data, outputs, runs hoặc models chỉ vì chúng có thể được tạo lại. Mọi cleanup cần user phê duyệt sau khi chứng minh nguồn backup còn tồn tại.

## 8. Điều chỉnh và cải tiến

Dùng manifest gồm đường dẫn nguồn, SHA-256, experiment ID, dataset version và nơi backup. Kiểm tra clone/rebuild trên môi trường sạch trước khi coi archive hoàn tất.

## 9. Kết luận tại thời điểm thực hiện

Dự án chưa được khóa tại ngày 29/08/2026. Ngày 20/10 là mốc kế hoạch, không phải sự kiện đã hoàn thành.

## 10. Minh chứng

- [Git evidence](../evidence/github_evidence.md)
- [Dataset evidence](../evidence/dataset_evidence.md)
- [Model evidence](../evidence/model_evidence.md)
- [Media Index](../MEDIA_INDEX.md)

## 11. Hình ảnh đề xuất

<!-- TODO_MEDIA:
source: future archive checklist and release page
timestamp: N/A
description: Final provenance map và trạng thái backup đã xác nhận
-->

## 12. Video minh họa

Tham chiếu V12 sau khi video cuối được upload; không tạo media mới chỉ cho bước archive.

## 13. Đóng góp của thành viên

`TO_VERIFY_WITH_STUDENTS`: xác nhận người kiểm tra archive, checksum, report và media.

## 14. Công việc tiếp theo

Sau khi toàn bộ checklist pass và user phê duyệt, mới tạo tag/release hoặc cleanup local như một bước riêng.
