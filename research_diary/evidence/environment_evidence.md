# Environment evidence

## Dữ liệu đầu vào

Hai sensor JSON mô tả hai phiên T2 `baseline`. Mỗi file chỉ có `sensor_at_start` và `sensor_at_end` với ba biến:

- `temperature`: 25 ở cả đầu và cuối của cả hai phiên;
- `ph`: 6,6 ở cả đầu và cuối của cả hai phiên;
- `light`: 203 → 200 ở phiên 1; 164 → 165 ở phiên 2.

Raw sensor nằm trong `data/raw/` và bị ignore; nhật ký không copy hoặc sửa chúng.

## Tích hợp

Experiment `TOP_ENV_BEHAVIOR_001` ghép context theo `video_id`, không nội suy sensor. Output gồm 382 cửa sổ cá thể và 167 cửa sổ nhóm.

Nguồn commit được xác minh: `dbc51a9fec769a9f1754d5ba479f5b77317b39fd`.

- [`Notebook 16`](../../notebooks/16_environment_behavior_analysis.ipynb)
- [`config.yaml`](../../logs/environment/TOP_ENV_BEHAVIOR_001/config.yaml)
- [`summary.json`](../../logs/environment/TOP_ENV_BEHAVIOR_001/summary.json)
- [`environment_session_summary.csv`](../../results/environment/environment_session_summary.csv)
- [`environment_behavior_comparison.csv`](../../results/environment/environment_behavior_comparison.csv)

## Sáu biểu đồ

1. [`top_environment_session_conditions.png`](../../results/environment/plots/top_environment_session_conditions.png)
2. [`top_individual_speed_comparison.png`](../../results/environment/plots/top_individual_speed_comparison.png)
3. [`top_individual_turning_path_efficiency.png`](../../results/environment/plots/top_individual_turning_path_efficiency.png)
4. [`top_group_nearest_neighbor_comparison.png`](../../results/environment/plots/top_group_nearest_neighbor_comparison.png)
5. [`top_group_dispersion_comparison.png`](../../results/environment/plots/top_group_dispersion_comparison.png)
6. [`top_group_polarization_comparison.png`](../../results/environment/plots/top_group_polarization_comparison.png)

## Giới hạn

Temperature và pH không thay đổi giữa hai phiên, nên không thể kiểm tra hiệu ứng. Light khác nhưng bị confound với session; chỉ có thể nói các descriptor hành vi khác nhau quan sát được giữa hai phiên.
