# Tracking evidence

## ByteTrack ablation Front

Ba cấu hình B15, B30 và B60 giữ cùng threshold và khác `track_buffer`. Trên video Front một cá có visibility ground truth, cả ba có visible track coverage khoảng 0,99914 và cùng một excess fragment; B15 được chọn tạm thời do buffer nhỏ hơn khi các quality diagnostic hòa nhau.

Nguồn: [`front_bytetrack_ablation.csv`](../../results/tracking/front_bytetrack_ablation.csv), [`summary.json`](../../logs/tracking/FRONT_BYTETRACK_ABLATION_001/summary.json).

## Tracker benchmark

ByteTrack B15 và BoT-SORT có quality diagnostic giống nhau trên video một cá; ByteTrack có processing FPS cao hơn trong log đó. Kết quả không chứng minh hiệu năng MOT nhiều cá.

Nguồn: [`front_tracker_benchmark.csv`](../../results/tracking/front_tracker_benchmark.csv), [`summary.json`](../../logs/tracking/FRONT_TRACKER_BENCHMARK_001/summary.json).

## MOT ground truth

File hiện có 200 frame được chọn và 768 GT object rows. HOTA chưa được tính trong summary. Chỉ segment `V3_FEEDING/F1_FEEDING_DENSE` có official status `OK`; các segment còn lại bị skip do identity uncertain. Không được tổng quát hóa các metric này thành độ chính xác toàn hệ thống.

Nguồn: [`FRONT_MOT_GT_EVAL_001/summary.json`](../../logs/tracking/FRONT_MOT_GT_EVAL_001/summary.json), [`front_mot_official_metrics_by_segment.csv`](../../results/tracking/front_mot_official_metrics_by_segment.csv).

## TOP tracking

TOP_VIDEO_1 và TOP_VIDEO_2 có nhiều ID ngắn và fragmentation đáng kể. Track ID là phạm vi video, không phải cá thể sinh học. Nguồn: [`top_bytetrack_baseline_summary.csv`](../../results/tracking/top_bytetrack_baseline_summary.csv).
