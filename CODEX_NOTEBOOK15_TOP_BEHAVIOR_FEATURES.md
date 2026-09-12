# CODEX SPEC — NOTEBOOK 15: TOP BEHAVIOR FEATURES
## Project: Nghiên cứu hành vi của cá bằng AI
## Repository: https://github.com/khkt-tn/fish
## Previous checkpoint: `4c582fc012f8e37bf7dd003e034aa7ee1676bed3`
## Previous checkpoint message: `checkpoint-14-top-detection-tracking`

---

# 0. MỤC TIÊU

Tạo và hoàn thiện:

```text
notebooks/15_top_behavior_features.ipynb
```

Notebook 15 là bước nối:

```text
Notebook 14
TOP detection + ByteTrack
        ↓
raw TOP tracks
        ↓
trajectory cleaning / segmentation
        ↓
individual 2D movement features
        ↓
instantaneous group descriptors
        ↓
5 s / 1 s synchronized feature windows
        ↓
evidence cho Notebook 16 sensor synchronization
```

Notebook 15 **không phải**:

- detector training;
- tracker tuning;
- behavior classification;
- cross-camera identity matching;
- sensor synchronization;
- biological diagnosis;
- stress/sickness inference;
- Raspberry Pi deployment.

Mục tiêu khoa học của Notebook 15 là biến tracking output đã được chốt ở Notebook 14 thành các **đại lượng định lượng mô tả chuyển động và tổ chức không gian của cá nhìn từ camera TOP**.

---

# 1. SOURCE OF TRUTH

Trước khi làm việc, Codex phải đọc:

```text
AGENTS.md
FISH_AI_PROJECT_WORKFLOW.md
CODEX_TOP_DATASET_PIPELINE.md
notebooks/14_top_detection_tracking.ipynb
logs/tracking/TOP_TRACK_BYTETRACK_B15_001/summary.json
results/tracking/top_bytetrack_baseline_summary.csv
notebooks/10_front_trajectory_cleaning.ipynb
notebooks/11_front_behavior_features.ipynb
```

Tham khảo thêm khi cần:

```text
notebooks/12_front_behavior_labeling.ipynb
notebooks/13_front_behavior_models.ipynb
```

Nhưng Notebook 12–13 chỉ để hiểu downstream requirements.

Không copy behavior labels/model của FRONT sang TOP.

---

# 2. TRẠNG THÁI ĐÃ CHỐT TỪ NOTEBOOK 14

Remote checkpoint đã được push:

```text
commit:
4c582fc012f8e37bf7dd003e034aa7ee1676bed3

message:
checkpoint-14-top-detection-tracking
```

TOP detector:

```text
decision = PASS

model:
runs/top/yolov8n_top_v2_baseline/weights/best.pt

model SHA-256:
216174c3a40d57bfd7b0d7e46eec90974ddb0b27c879dd1961543e3233a6c5e5

Precision:
0.967530547941785

Recall:
0.9713393817483137

mAP50:
0.9834169324420174

mAP50-95:
0.6062227869655318
```

TOP tracker:

```text
decision = PASS_WITH_WARNING

config:
configs/trackers/top_bytetrack_b15.yaml
```

Actual config:

```yaml
tracker_type: bytetrack
track_high_thresh: 0.68
track_low_thresh: 0.50
new_track_thresh: 0.68
track_buffer: 15
match_thresh: 0.80
fuse_score: true
```

Trajectory:

```text
usable = YES
```

Do not retrain or retrack in Notebook 15.

---

# 3. INPUT VIDEOS VÀ TRACKING ARTIFACTS

Videos:

```text
data/raw/top/1.mp4
data/raw/top/2.mp4
```

N14 video identifiers:

```text
1.mp4 → TOP_VIDEO_1
2.mp4 → TOP_VIDEO_2
```

Raw tracking input:

```text
outputs/top/tracking/1_tracking_raw.csv
outputs/top/tracking/2_tracking_raw.csv
```

Overlay is NOT an analytical input:

```text
outputs/top/tracking/1_tracking_overlay.mp4
outputs/top/tracking/2_tracking_overlay.mp4
```

Do not require overlays to calculate features.

---

# 4. INPUT HASH GATE

Notebook 15 must read:

```text
logs/tracking/TOP_TRACK_BYTETRACK_B15_001/summary.json
```

and verify raw tracking file hashes before analysis.

Expected:

```text
1_tracking_raw.csv
SHA256 =
9fa203913d994ca0b25658c6d4d88ddd1d0d46e0b3e19a9ce7a06732e144373f
```

```text
2_tracking_raw.csv
SHA256 =
500323ccb3d928c2f8953e90321877d93c1562cef8b1c627dc845f2048c764f6
```

Video hashes already recorded:

```text
1.mp4 =
57d09e2c4613fc383c2532d36f53bf15866409673ba2743f19a0574252606865

2.mp4 =
a92642426eb4a10d4390613a540cdc5a5374e22656b05e773c93f7fb1208274b
```

## Rule

If raw tracking CSV hash differs:

```text
HOLD
```

Do not silently continue using an unverified tracking artifact.

Do not rerun tracker automatically.

Report the mismatch and STOP.

---

# 5. N14 TRACKING LIMITATIONS PHẢI ĐƯỢC KẾ THỪA

Notebook 15 must preserve these scientific limitations:

## 1.mp4

```text
duration ≈ 57.83 s
median active tracks/frame = 2
unique track IDs = 33
median lifespan ≈ 1.29 s
tracks >= 5 s = 7
gap events = 38
```

## 2.mp4

```text
duration ≈ 118.27 s
median active tracks/frame = 3
unique track IDs = 53
median lifespan ≈ 0.76 s
tracks >= 5 s = 20
gap events = 52
```

Interpretation:

> Significant identity fragmentation/proliferation exists.

Therefore:

```text
Track ID ≠ biological identity
```

and:

```text
TOP_VIDEO_1 Track 5 ≠ TOP_VIDEO_2 Track 5
```

and:

```text
FRONT Track 5 ≠ TOP Track 5
```

Notebook 15 must never imply otherwise.

---

# 6. KEY DESIGN DECISION — DO NOT STITCH DIFFERENT TRACK IDs

This is mandatory.

Do NOT implement heuristic re-identification such as:

```text
if Track 17 ends near Track 24 → join them
```

Do NOT join IDs using:

```text
nearest position
same size
same color
same direction
small time gap
```

Do NOT try to “repair” fragmentation by merging different IDs.

Reason:

Without identity ground truth or validated ReID, this would create invented biological identities.

Notebook 15 may only:

1. segment within the SAME tracker ID;
2. interpolate very short gaps within the SAME tracker ID;
3. smooth within the SAME trajectory segment.

---

# 7. NOTEBOOK EXECUTION POLICY

According to `AGENTS.md`:

Codex prepares Notebook 15.

USER executes Notebook 15 manually in VS Code.

Codex must NOT:

```text
jupyter nbconvert --execute
papermill
automated Run All
```

Codex may perform static validation only.

After preparation:

```text
STOP
```

User selects kernel:

```text
fish
/home/diy-hus/miniconda3/envs/fish/bin/python
```

and runs manually.

---

# 8. ENVIRONMENT

Use:

```text
conda env = fish
```

Do not use:

```text
fish-export
```

Notebook 15 does not require CUDA.

CUDA status may be logged but is not a blocker because this stage is trajectory/feature processing.

Do not create a new environment.

Do not broad-upgrade packages.

---

# 9. PROJECT PATH POLICY

Do not hard-code:

```text
/home/diy-hus/fish
```

Use repository-root resolution.

Preferred:

```python
from pathlib import Path

def find_project_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (
            (candidate / "AGENTS.md").exists()
            and (candidate / "FISH_AI_PROJECT_WORKFLOW.md").exists()
            and (candidate / ".git").exists()
        ):
            return candidate
    raise RuntimeError("Cannot resolve PROJECT_ROOT")

PROJECT_ROOT = find_project_root(Path.cwd())
```

---

# 10. NOTEBOOK 15 STRUCTURE

Recommended cell/section order:

```text
0. Title and scientific objective
1. Provenance and environment
2. CONFIG
3. Input/hash validation
4. Raw tracking schema audit
5. Trajectory segmentation
6. Short-gap interpolation
7. Trajectory smoothing
8. Cleaning QC
9. Step-level kinematics
10. Frame-relative spatial descriptors
11. Instantaneous social/group descriptors
12. Global synchronized 5 s / 1 s window grid
13. Individual window features
14. Group window features
15. Feature QC
16. Visualization
17. Feature schema
18. Evidence/log export
19. Scientific interpretation
20. Final decision
21. Next step
```

---

# 11. EXPERIMENT IDs

Use two internal provenance stages within Notebook 15.

Trajectory stage:

```text
TOP_TRAJECTORY_CLEANING_001
```

Feature stage:

```text
TOP_BEHAVIOR_FEATURES_001
```

This preserves traceability:

```text
N14 raw tracks
↓
TOP_TRAJECTORY_CLEANING_001
↓
TOP_BEHAVIOR_FEATURES_001
↓
N16
```

---

# 12. OUTPUT DATA POLICY

Do NOT repeat the FRONT mistake of putting a large full trajectory CSV in a committable results path.

Full local analytical data should go under ignored `outputs/`.

## Local full trajectory

Preferred:

```text
outputs/top/trajectory/top_cleaned_trajectories.parquet
```

Fallback if Parquet dependency is unavailable:

```text
outputs/top/trajectory/top_cleaned_trajectories.csv
```

Do not install a large dependency solely to force Parquet.

## Local individual feature table

Preferred:

```text
outputs/top/behavior/top_individual_window_features.parquet
```

Fallback:

```text
outputs/top/behavior/top_individual_window_features.csv
```

## Local group feature table

Preferred:

```text
outputs/top/behavior/top_group_window_features.parquet
```

Fallback:

```text
outputs/top/behavior/top_group_window_features.csv
```

Full local artifacts are not committed.

---

# 13. COMMITTABLE RESEARCH EVIDENCE

Small evidence:

```text
results/trajectory/top_trajectory_cleaning_summary.csv
results/trajectory/top_trajectory_segment_summary.csv

results/behavior/top_feature_summary.csv
results/behavior/top_feature_qc_summary.csv
results/behavior/top_group_feature_summary.csv
results/behavior/top_behavior_feature_schema.json
```

Logs:

```text
logs/trajectory/TOP_TRAJECTORY_CLEANING_001/
├── config.yaml
├── environment.txt
└── summary.json
```

```text
logs/behavior/TOP_BEHAVIOR_FEATURES_001/
├── config.yaml
├── environment.txt
└── summary.json
```

Optional small plots:

```text
results/behavior/plots/top_*.png
```

Do not commit large raw feature tables unless their actual size is confirmed small and user explicitly approves.

---

# 14. RAW TRACKING SCHEMA AUDIT

Do not assume column spelling from memory.

Load actual CSVs and inspect:

```python
df.columns.tolist()
df.dtypes
```

Required semantic fields:

```text
video identifier
source video
frame index
time seconds
track ID
bbox x1,y1,x2,y2
center x,y
confidence
frame width
frame height OR recoverable video dimensions
normalized center coordinates OR derivable center coordinates
```

If aliases differ, normalize into a canonical schema.

Canonical recommended names:

```text
video_id
source_video
frame_index
time_sec
track_id
confidence
x1
y1
x2
y2
cx
cy
cx_norm
cy_norm
frame_width
frame_height
fps_source
```

Validate uniqueness:

```text
(video_id, frame_index, track_id)
```

Duplicate keys are a blocker unless explained.

---

# 15. TRAJECTORY SEGMENTATION

Work independently per:

```text
video_id
track_id
```

Sort by:

```text
frame_index
```

For two consecutive observed points:

```python
frame_diff = current_frame - previous_frame
missing_frames = frame_diff - 1
```

Use:

```text
MAX_INTERP_GAP_FRAMES = 3
```

matching the accepted FRONT cleaning logic.

Rules:

```text
missing_frames = 0
→ same segment, contiguous

1 <= missing_frames <= 3
→ same segment, eligible for interpolation

missing_frames > 3
→ start a NEW trajectory segment
```

Do not bridge the gap.

Create stable:

```text
trajectory_uid
```

Example concept:

```text
TOP_VIDEO_1_track_17_seg_03
```

---

# 16. SHORT-GAP INTERPOLATION

Only inside one trajectory UID.

For gaps of 1–3 frames:

Linearly interpolate:

```text
cx
cy
```

and optionally bbox geometry if needed.

Create:

```text
observed
interpolated
```

with exactly:

```text
original row:
observed = True
interpolated = False

inserted row:
observed = False
interpolated = True
```

Confidence for interpolated rows:

Prefer:

```text
NaN
```

Do not invent detector confidence.

---

# 17. GROUP METRICS MUST NOT TREAT INTERPOLATION AS OBSERVED FISH PRESENCE

This rule is critical.

Individual movement features may use short-gap interpolation.

But instantaneous group/social descriptors must use:

```text
observed == True
```

by default.

Reason:

Interpolated positions are useful to smooth a trajectory but should not silently create an observed individual in group-count or social-distance calculations.

If a sensitivity table using interpolated positions is later desired, keep it secondary and explicitly labeled.

Primary group metrics:

```text
observed rows only
```

---

# 18. SMOOTHING

Match FRONT principle:

```text
SMOOTH_WINDOW_FRAMES = 5
```

Use centered rolling median within each trajectory UID.

Smooth:

```text
cx
cy
```

to:

```text
cx_clean
cy_clean
```

Do not smooth across:

```text
different trajectory_uid
different track ID
different video
```

Do not apply heavy splines or polynomial smoothing.

Rationale:

Reduce bbox jitter without suppressing true large-scale movement.

Record that 5 frames correspond to slightly different time spans because TOP videos have different FPS.

---

# 19. MINIMUM SEGMENT QC

Config:

```text
MIN_SEGMENT_POINTS = 5
```

But a 5-point segment is not automatically valid for a 5-second behavior window.

Keep segment-level fields:

```text
segment_n_points
segment_start_sec
segment_end_sec
segment_duration_sec
observed_ratio
interpolated_ratio
```

Report distributions.

---

# 20. STEP-LEVEL KINEMATICS

Calculate inside each trajectory UID using actual timestamps.

For successive cleaned points:

```text
dt
dx
dy
step_distance_px
speed_px_s
```

Image diagonal:

```python
diag_px = hypot(frame_width, frame_height)
```

Normalized:

```text
step_distance_diag
speed_diag_s
```

Do not call normalized diagonal units:

```text
cm
m
cm/s
m/s
```

Physical calibration does not exist yet.

---

# 21. TURNING / DIRECTION

Heading:

```python
heading = atan2(dy, dx)
```

Wrapped turning angle:

```python
dtheta = wrap_to_pi(theta_t - theta_previous)
```

Useful outputs:

```text
mean_abs_turn_rad
median_abs_turn_rad
p95_abs_turn_rad
cumulative_abs_turn_rad
turn_rate_rad_s
heading_resultant_length
```

`heading_resultant_length`:

```text
0 → headings dispersed
1 → headings strongly aligned within the trajectory window
```

This is a movement-direction descriptor.

Do not assign a behavior label from it.

---

# 22. PATH DESCRIPTORS

For each window:

```text
path_length_px
path_length_diag
net_displacement_px
net_displacement_diag
path_efficiency
```

where:

```text
path_efficiency = net_displacement / path_length
```

Interpret:

```text
near 1 → straighter path
lower → more winding path
```

Do not use an ambiguous variable name `tortuosity` unless a precise mathematical definition is included.

Prefer explicit metrics above.

---

# 23. SPEED / ACCELERATION DESCRIPTORS

Recommended:

```text
mean_speed_px_s
median_speed_px_s
max_speed_px_s
p95_speed_px_s
speed_std_px_s

mean_speed_diag_s
median_speed_diag_s
max_speed_diag_s

mean_abs_accel_px_s2
p95_abs_accel_px_s2
mean_abs_accel_diag_s2
```

Acceleration amplifies tracking noise.

Therefore:

- compute from cleaned trajectory;
- retain QC;
- do not overinterpret.

---

# 24. SPATIAL POSITION — NO FALSE TANK CALIBRATION

Current data do NOT contain a validated tank geometry calibration.

Therefore primary spatial variables must be named:

```text
frame-relative
```

not:

```text
tank-relative
wall distance
physical wall-following
```

Recommended continuous descriptors:

```text
x_mean_norm
x_std_norm
x_range_norm

y_mean_norm
y_std_norm
y_range_norm

mean_distance_to_frame_center_diag
median_distance_to_frame_center_diag

mean_distance_to_nearest_frame_edge_min_dim
median_distance_to_nearest_frame_edge_min_dim
```

Distance to center:

```python
sqrt((cx - width/2)^2 + (cy - height/2)^2) / image_diagonal
```

Distance to nearest frame edge:

```python
min(cx, width-cx, cy, height-cy) / min(width, height)
```

---

# 25. FRAME CENTER / PERIMETER DESCRIPTIVE ZONES

Optional descriptive zones are allowed if clearly named as IMAGE/FRAME zones.

Config example:

```text
FRAME_EDGE_BAND_FRACTION = 0.10
CENTER_BOX_MARGIN_FRACTION = 0.25
```

Meaning:

```text
frame edge band:
within 10% of min(frame width, frame height) from image border

center box:
x in [0.25, 0.75]
y in [0.25, 0.75]
```

Feature names must include `frame`:

```text
frame_edge_band_ratio
frame_center_box_ratio
```

Do NOT name these:

```text
wall_following_ratio
tank_perimeter_ratio
```

until the real tank boundary is validated.

---

# 26. OPTIONAL ARENA GEOMETRY

Include a future-compatible CONFIG:

```python
ARENA_GEOMETRY = None
```

Notebook may generate representative frame plots to help future calibration.

If `ARENA_GEOMETRY is None`:

```text
wall_metrics_available = False
```

Do not fail Notebook 15.

If later user explicitly supplies validated tank ROI/boundary, wall metrics may be added in a new controlled experiment.

Do not infer tank boundary automatically in this checkpoint.

---

# 27. NEAREST-NEIGHBOR DISTANCE

For each observed frame with N >= 2 active tracks:

For each track i:

```text
NND_i = min distance(i,j), j != i
```

Use Euclidean center distance.

Store both:

```text
nearest_neighbor_distance_px
nearest_neighbor_distance_diag
```

For individual windows aggregate:

```text
mean_nnd_diag
median_nnd_diag
min_nnd_diag
neighbor_observation_ratio
```

where:

```text
neighbor_observation_ratio
=
fraction of the individual's observed rows for which at least one other active track exists
```

Do not invent NND when only one track is observed.

Use NaN.

---

# 28. PAIRWISE DISTANCE

For an observed frame with N >= 2:

Compute all unique pairs:

```text
i < j
```

Frame-level:

```text
mean_pairwise_distance_diag
median_pairwise_distance_diag
min_pairwise_distance_diag
max_pairwise_distance_diag
```

These are tracker-observed spatial proximity descriptors.

Because true fish count is not known, do not claim that all biological individuals are present.

---

# 29. GROUP CENTROID

For observed active track centers:

```python
centroid_x = mean(cx)
centroid_y = mean(cy)
```

Normalized:

```text
group_centroid_x_norm
group_centroid_y_norm
```

Use for spatial position.

Be cautious with group centroid velocity because active tracker composition changes through fragmentation.

Do not make group-centroid speed a primary metric in this checkpoint.

---

# 30. GROUP DISPERSION

Recommended frame-level group spread descriptors:

```text
group_rms_radius_diag
group_bbox_area_ratio
group_convex_hull_area_ratio
```

RMS radius:

```text
sqrt(mean(distance(point_i, centroid)^2)) / image_diagonal
```

Bounding rectangle group area:

```text
(max_x-min_x)*(max_y-min_y) / frame_area
```

Convex hull:

```text
N >= 3 → convex hull area / frame_area
N < 3 → NaN
```

Do not pretend hull area is meaningful for N < 3.

---

# 31. GROUP POLARIZATION / ALIGNMENT

Scientific basis:

Group polarization can be described as:

```text
P = | mean(unit velocity vectors) |
```

with:

```text
0 <= P <= 1
```

Compute only when:

```text
at least 2 active observed tracks
AND
at least 2 have valid non-zero instantaneous velocity vectors
```

Use velocity derived within each trajectory UID.

Do not calculate velocity across segment boundaries.

Output:

```text
group_polarization
n_valid_headings
```

Interpret only as movement alignment.

Do not equate directly with a named biological state.

---

# 32. ACTIVE TRACK COUNT IS NOT FISH COUNT

Use exact name:

```text
n_active_tracks
```

Do not use:

```text
n_fish
fish_count
```

because true fish count is unavailable and identity fragmentation exists.

Group metrics must carry this limitation.

---

# 33. GLOBAL WINDOW GRID — IMPORTANT FOR NOTEBOOK 16

Use synchronized windows based on video time, not independent track-relative windows.

Default:

```text
WINDOW_SEC = 5.0
STEP_SEC = 1.0
```

For each video:

```text
window [0,5)
window [1,6)
window [2,7)
...
```

until the final full 5-second window.

This ensures:

- individual features align to group features;
- future sensor synchronization uses common timestamps;
- windows are comparable across active tracks.

Use:

```text
window_start_sec
window_end_sec
window_mid_sec
```

---

# 34. INDIVIDUAL WINDOW COVERAGE

Keep compatibility with FRONT:

```text
MIN_WINDOW_COVERAGE = 0.60
```

Expected points should be derived from:

```text
window duration × source FPS
```

Output:

```text
n_points
coverage_ratio
observed_ratio
interpolated_ratio
window_time_span_sec
```

Do not hide low coverage.

A feature row is generated only if:

```text
coverage_ratio >= 0.60
```

and there are enough points for movement calculations.

Do not call a 60%-covered window “complete”.

---

# 35. INDIVIDUAL WINDOW FEATURE SCHEMA

Minimum identifiers:

```text
camera
video_id
source_video
trajectory_uid
track_id
window_start_sec
window_end_sec
window_mid_sec
fps_source
```

Quality:

```text
n_points
coverage_ratio
observed_ratio
interpolated_ratio
window_time_span_sec
mean_detection_confidence
```

Movement:

```text
path_length_px
path_length_diag
distance_last_1s_px
distance_last_1s_diag
net_displacement_px
net_displacement_diag
path_efficiency

mean_speed_px_s
median_speed_px_s
max_speed_px_s
p95_speed_px_s
speed_std_px_s

mean_speed_diag_s
median_speed_diag_s
max_speed_diag_s

mean_abs_accel_px_s2
p95_abs_accel_px_s2
mean_abs_accel_diag_s2
```

Turning:

```text
mean_abs_turn_rad
median_abs_turn_rad
p95_abs_turn_rad
cumulative_abs_turn_rad
turn_rate_rad_s
heading_resultant_length
```

Spatial:

```text
x_mean_norm
x_std_norm
x_range_norm
y_mean_norm
y_std_norm
y_range_norm

mean_distance_to_frame_center_diag
median_distance_to_frame_center_diag
mean_distance_to_nearest_frame_edge_min_dim
median_distance_to_nearest_frame_edge_min_dim

frame_edge_band_ratio
frame_center_box_ratio
```

Social proximity:

```text
mean_nnd_diag
median_nnd_diag
min_nnd_diag
neighbor_observation_ratio
```

---

# 36. GROUP FRAME-LEVEL FEATURE SCHEMA

Per observed frame:

```text
video_id
source_video
frame_index
time_sec
n_active_tracks

group_centroid_x_norm
group_centroid_y_norm

mean_nnd_diag
median_nnd_diag

mean_pairwise_distance_diag
median_pairwise_distance_diag
min_pairwise_distance_diag
max_pairwise_distance_diag

group_rms_radius_diag
group_bbox_area_ratio
group_convex_hull_area_ratio

group_polarization
n_valid_headings
```

Frame metrics should be intermediate local data.

Do not necessarily commit this full table.

---

# 37. GROUP WINDOW FEATURE SCHEMA

Aggregate frame-level descriptors over the same 5 s / 1 s windows.

Identifiers:

```text
camera
video_id
source_video
window_start_sec
window_end_sec
window_mid_sec
```

Coverage:

```text
expected_frames
frames_with_any_track
group_frame_coverage
frames_with_2plus_tracks
social_metric_frame_ratio
```

Track activity:

```text
mean_active_tracks
median_active_tracks
min_active_tracks
max_active_tracks
```

Group spatial:

```text
mean_group_centroid_x_norm
mean_group_centroid_y_norm

mean_nnd_diag
median_nnd_diag

mean_pairwise_distance_diag
median_pairwise_distance_diag

mean_group_rms_radius_diag
median_group_rms_radius_diag

mean_group_bbox_area_ratio
mean_group_convex_hull_area_ratio

mean_group_polarization
median_group_polarization
polarization_valid_frame_ratio
```

---

# 38. GROUP FEATURE QUALITY RULES

Do not output misleading zeros.

Examples:

```text
N < 2:
NND = NaN
pairwise distance = NaN
polarization = NaN

N < 3:
convex hull area = NaN
```

Use:

```text
NaN
```

not zero.

A zero has biological/geometric meaning and must not represent missing data.

---

# 39. SOCIAL METRIC LIMITATION

Because identity fragmentation exists:

- instantaneous pairwise geometry is generally usable;
- long-duration individual social identity is not established;
- do not infer stable dyads;
- do not infer individual preference for a specific conspecific;
- do not infer social network identity.

Notebook 15 is limited to short-window spatial descriptors.

---

# 40. OCCUPANCY / HEATMAP

Generate descriptive occupancy plots per video using:

```text
observed cleaned positions
```

Prefer normalized coordinates.

Do not combine two videos into one heatmap unless clearly labeled.

Plot:

```text
x_norm vs y_norm occupancy density
```

Use fixed axes:

```text
x: 0 to 1
y: 0 to 1
```

Account for image coordinate convention:

```text
y increases downward
```

Either invert plotted y-axis to match physical visual orientation or label clearly.

---

# 41. REPRESENTATIVE TRAJECTORY QC PLOTS

Plot a small number of representative segments:

- long segment;
- medium segment;
- segment containing short interpolation;
- do not cherry-pick only aesthetically good tracks.

Overlay:

```text
raw observed centers
interpolated points
cleaned path
```

Purpose:

verify cleaning, not demonstrate behavior.

---

# 42. FEATURE DISTRIBUTION QC

At minimum inspect distributions per video for:

```text
coverage_ratio
observed_ratio
segment duration
mean_speed_diag_s
path_efficiency
mean_abs_turn_rad
mean_nnd_diag
group_polarization
group_rms_radius_diag
```

Check:

```text
NaN rate
inf rate
impossible values
extreme outliers
```

Do not auto-delete statistical outliers just because they are extreme.

Flag them first.

---

# 43. HARD VALIDITY CHECKS

Examples:

```text
coverage_ratio in [0,1]
observed_ratio in [0,1]
interpolated_ratio in [0,1]

path_length >= 0
speed >= 0
NND >= 0
pairwise distance >= 0

path_efficiency generally in [0,1] within numerical tolerance

group_polarization in [0,1]

area ratios >= 0
```

If values violate mathematical constraints materially:

```text
HOLD
```

Investigate code.

---

# 44. DO NOT CALIBRATE PHYSICAL UNITS

Current Notebook 15 outputs remain:

```text
pixels
pixels/second
image-diagonal normalized units
frame-normalized coordinates
```

Do not output:

```text
cm
cm/s
m
m/s
```

unless a separate verified geometric calibration is supplied.

---

# 45. DO NOT LABEL BEHAVIOR

Notebook 15 must not create labels such as:

```text
NORMAL_SWIM
FEEDING
PAIR_INTERACTION
STRESS
SICK
ANXIOUS
AGGRESSIVE
```

from feature thresholds.

It only computes descriptive features.

Behavior labeling requires separate ground truth / downstream design.

---

# 46. CONTEXT / T1-T2

Current N14 evidence says:

```text
T1/T2 unavailable from exported metadata
```

Do not infer:

```text
1.mp4 = T1
2.mp4 = T2
```

unless user explicitly provides this mapping.

Recommended field:

```text
experimental_context = UNKNOWN
```

or null.

Do not use filename number as biological condition.

---

# 47. N15 FEATURE SUMMARY

Create small committable summary per video.

Suggested columns:

```text
video_id
source_video
raw_tracking_rows
unique_raw_track_ids
trajectory_segments
cleaned_rows
observed_rows
interpolated_rows
segments_ge_5s
individual_windows
median_individual_coverage
median_mean_speed_diag_s
median_path_efficiency
median_mean_abs_turn_rad
median_mean_nnd_diag
group_windows
median_active_tracks
median_group_nnd_diag
median_group_pairwise_distance_diag
median_group_rms_radius_diag
median_group_polarization
warnings
```

Do not aggregate away all video-specific information.

---

# 48. TRAJECTORY CLEANING SUMMARY

For each video record:

```text
raw rows
unique raw track IDs
gap events
interpolated gap count
interpolated rows
segments created
segments discarded
cleaned rows
median segment duration
p95 segment duration
max segment duration
segments >= 5 s
```

This is critical because fragmentation affects downstream features.

---

# 49. FEATURE SCHEMA JSON

Create:

```text
results/behavior/top_behavior_feature_schema.json
```

For every field include:

```text
name
level
unit
definition
source
missingness rule
scientific caution
```

Levels:

```text
individual_window
group_frame
group_window
quality
identifier
```

Example unit:

```text
px
px/s
diag
diag/s
rad
rad/s
ratio
count
seconds
```

This schema will support Notebook 16 and final paper writing.

---

# 50. PROVENANCE IN SUMMARY.JSON

`TOP_TRAJECTORY_CLEANING_001/summary.json` should record:

```text
experiment_id
datetime
git commit
input raw tracking paths
input raw tracking SHA256
N14 experiment ID
tracker config
tracker config SHA256
cleaning config
output paths
output SHA256
per-video QC
warnings
decision
```

`TOP_BEHAVIOR_FEATURES_001/summary.json` should record:

```text
experiment_id
datetime
git commit
input cleaned trajectory SHA256
window_sec
step_sec
coverage threshold
feature groups
output paths
output SHA256
row counts
per-video summary
NaN summary
warnings
decision
next step
```

---

# 51. SCIENTIFIC BASIS

Notebook 15 should include a short Markdown rationale, not a literature review.

Recognized fish/group movement descriptors include:

```text
speed
nearest-neighbor distance
group polarization/alignment
group centroid
pairwise distances
spatial dispersion
```

The project uses these as quantitative descriptors, not direct diagnoses.

Useful references for methodological rationale:

1. **Dominating lengthscales of zebrafish collective behaviour**
   PLOS Computational Biology, 2021.
   DOI: 10.1371/journal.pcbi.1009394
   Uses average speed, polarization and nearest-neighbor distance as collective descriptors.

2. **Consistent Individual Differences Drive Collective Behavior and Group Functioning of Schooling Fish**
   Scientific Reports / open-access PMC record.
   Provides definitions for nearest-neighbor distance and group center.

3. General animal movement literature recognizes:
   step length, speed, turning angle, path length and displacement as basic movement descriptors.

Do not claim these references validate the project's behavior labels.

---

# 52. EXPECTED NOTEBOOK DECISION

Likely final state, if calculations pass:

```text
TOP trajectory cleaning:
PASS_WITH_WARNING

TOP individual features:
PASS_WITH_WARNING

TOP group features:
PASS_WITH_WARNING

Geometry calibration:
NOT AVAILABLE

Biological identity:
NOT ESTABLISHED

Features usable for Notebook 16:
YES

Notebook 15:
PASS_WITH_WARNING
```

Warning is expected because identity fragmentation remains.

A warning is not a failure if feature extraction respects segmentation and missingness.

---

# 53. HOLD CONDITIONS

Notebook 15 must HOLD if any of these occur:

1. N14 raw tracking hash mismatch.
2. Required tracking columns cannot be recovered.
3. Duplicate `(video, frame, track_id)` rows cannot be explained.
4. Cleaning crosses different track IDs.
5. Non-finite/invalid calculations are widespread due to code errors.
6. No trajectory segment supports useful movement windows.
7. Group metric mathematical constraints fail.
8. Output provenance cannot be traced to N14.
9. Code invents physical units or biological identity.

Do not patch around these silently.

---

# 54. PASS_WITH_WARNING CONDITIONS

Pass with warning is appropriate when:

- identity fragmentation remains;
- enough valid trajectory segments exist;
- individual windows are computable;
- group frame metrics are computable on sufficient observed frames;
- hashes/provenance pass;
- missing social metrics are correctly NaN;
- no physical calibration is claimed.

---

# 55. N16 READINESS

Notebook 16 needs time-aligned features.

Therefore N15 must guarantee:

```text
video_id
source_video
window_start_sec
window_end_sec
window_mid_sec
```

in both:

```text
individual feature table
group feature table
```

N16 can later align these with sensor timestamps.

Do not perform the alignment in N15.

---

# 56. GIT POLICY

Before work:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git log -1 --oneline
```

Expected remote checkpoint:

```text
4c582fc checkpoint-14-top-detection-tracking
```

But do not reset if local has valid changes.

Preserve unrelated pre-existing changes.

Do not use:

```bash
git add .
git add -A
git reset --hard
git clean -fd
```

Do not commit in the notebook-preparation step unless user explicitly requests.

---

# 57. EXISTING UNRELATED LOCAL CHANGES

Previous workflow reported these uncommitted files:

```text
notebooks/02_dataset_detection_audit.ipynb
notebooks/04_yolo_detection_evaluation.ipynb
notebooks/06a_front_visibility_groundtruth.ipynb
notebooks/13_front_behavior_models.ipynb
results/trajectory/front_cleaned_trajectories.csv
```

Codex must check current status.

If they remain:

- preserve;
- do not stage;
- do not revert;
- do not overwrite.

---

# 58. NOTEBOOK PREPARATION ACCEPTANCE CRITERIA

Before telling user to run:

```text
[ ] N15 notebook exists
[ ] kernel metadata = fish
[ ] no execution outputs fabricated
[ ] project root is relative/resolved
[ ] raw tracking paths are correct
[ ] hash verification code exists
[ ] N14 summary provenance is read
[ ] no detector/tracker rerun code executes automatically
[ ] no cross-ID stitching
[ ] short-gap interpolation only same ID
[ ] centered median smoothing within segment
[ ] group primary metrics use observed rows only
[ ] global 5 s / 1 s windows
[ ] individual schema complete
[ ] group schema complete
[ ] NaN rules correct
[ ] no cm/cm-s
[ ] no behavior labels
[ ] no T1/T2 guessing
[ ] full outputs go under outputs/
[ ] small evidence goes under results/logs
[ ] static notebook validation passes
```

---

# 59. USER EXECUTION FLOW

After Codex prepares Notebook 15:

User:

1. opens:

```text
notebooks/15_top_behavior_features.ipynb
```

2. selects kernel:

```text
fish
```

3. runs first provenance/preflight cells.

4. verifies:

```text
raw tracking hashes = PASS
```

5. then runs remaining notebook manually.

Codex does not run it for the user.

---

# 60. POST-RUN AUDIT

After user saves the executed notebook and reports completion, Codex should:

1. recompute selected metrics from local full outputs;
2. verify row counts;
3. verify output hashes;
4. verify mathematical bounds;
5. compare summaries with notebook;
6. ensure no fake outputs;
7. write/finalize evidence;
8. recommend:

```text
PASS
PASS_WITH_WARNING
HOLD
```

9. STOP before commit.

---

# 61. CHECKPOINT 15

Only after user reviews post-run evidence.

Suggested commit:

```text
checkpoint-15-top-behavior-features
```

Potential committable files:

```text
notebooks/15_top_behavior_features.ipynb

logs/trajectory/TOP_TRAJECTORY_CLEANING_001/
logs/behavior/TOP_BEHAVIOR_FEATURES_001/

results/trajectory/top_trajectory_cleaning_summary.csv
results/trajectory/top_trajectory_segment_summary.csv

results/behavior/top_feature_summary.csv
results/behavior/top_feature_qc_summary.csv
results/behavior/top_group_feature_summary.csv
results/behavior/top_behavior_feature_schema.json

small evidence plots if appropriate
```

Do NOT commit automatically:

```text
outputs/top/trajectory/
outputs/top/behavior/
data/
runs/
videos
models
large CSV/Parquet
```

---

# 62. FINAL REPORT FORMAT — BEFORE USER RUN

Codex must return:

## Repository

```text
Branch:
HEAD:
Remote status:
Working tree:
```

## N14 input provenance

```text
N14 checkpoint:
Tracking experiment:
1_tracking_raw hash:
2_tracking_raw hash:
Hash status:
```

## Notebook 15

```text
Path:
Cells:
Kernel:
Static validation:
```

## Feature design

```text
Trajectory cleaning:
Individual windows:
Group windows:
Physical units:
Arena geometry:
Identity handling:
```

## Files created/modified

```text
...
```

## User action

```text
Open notebooks/15_top_behavior_features.ipynb
Select fish kernel
Run manually
```

Then:

```text
STOP
```

---

# 63. FINAL REPORT FORMAT — AFTER USER RUN

Return:

## Trajectory QC

```text
1.mp4:
raw IDs:
segments:
interpolated rows:
segments >= 5 s:
cleaned rows:

2.mp4:
...
```

## Individual feature windows

```text
1.mp4:
window rows:
median coverage:
median speed:
median path efficiency:
median turning:
median NND:

2.mp4:
...
```

## Group feature windows

```text
1.mp4:
windows:
median active tracks:
median NND:
median pairwise distance:
median group radius:
median polarization:

2.mp4:
...
```

## QC

```text
NaN rates:
Invalid bounds:
Hash checks:
Warnings:
```

## Decision

```text
Trajectory:
Individual features:
Group features:
Notebook 15:
Ready for N16:
```

Then STOP before commit.

---

# 64. KEY SCIENTIFIC INTERPRETATION RULES

Allowed:

```text
higher mean speed
lower nearest-neighbor distance
higher polarization
greater spatial dispersion
more winding trajectory
greater frame-edge occupancy
```

Not allowed without further ground truth:

```text
fish is stressed
fish is sick
fish is happy
fish is anxious
fish is aggressive
fish is feeding
stable social pair
same biological fish across fragmented IDs
```

Descriptions are not diagnoses.

---

# 65. CORE RULE SUMMARY

Codex must preserve these rules above all else:

```text
N14 raw tracks are the input.
Do not rerun detector/tracker.
Verify hashes.
Never stitch different Track IDs.
Only interpolate <=3 missing frames within same ID.
Smooth within trajectory segment only.
Use observed rows for primary group metrics.
Use 5 s windows / 1 s step.
Use global video-time windows.
Keep physical units uncalibrated.
Do not call frame edge a tank wall.
Do not guess T1/T2.
Do not label behavior.
Do not infer biological identity.
Full tables stay local under outputs/.
Small evidence goes to results/logs.
User runs notebook manually.
Stop before commit.
```

---

# 66. PROMPT FOR CODEX

Use the prompt below after placing this specification in the repository root as:

```text
CODEX_NOTEBOOK15_TOP_BEHAVIOR_FEATURES.md
```

The prompt is intentionally shorter than the specification. Codex must read this full file before implementation.


```text
Continue the Fish AI research project from the accepted and pushed checkpoint:

4c582fc012f8e37bf7dd003e034aa7ee1676bed3
checkpoint-14-top-detection-tracking

Your current task is to PREPARE, but NOT EXECUTE:

notebooks/15_top_behavior_features.ipynb

Before modifying anything, read and follow:

AGENTS.md
FISH_AI_PROJECT_WORKFLOW.md
CODEX_NOTEBOOK15_TOP_BEHAVIOR_FEATURES.md
notebooks/14_top_detection_tracking.ipynb
logs/tracking/TOP_TRACK_BYTETRACK_B15_001/summary.json
results/tracking/top_bytetrack_baseline_summary.csv
notebooks/10_front_trajectory_cleaning.ipynb
notebooks/11_front_behavior_features.ipynb

The detailed requirements in CODEX_NOTEBOOK15_TOP_BEHAVIOR_FEATURES.md are authoritative for Notebook 15 unless they conflict with AGENTS.md or the project workflow.

CURRENT ACCEPTED N14 INPUTS

TOP videos:
data/raw/top/1.mp4
data/raw/top/2.mp4

Verified raw tracking inputs:
outputs/top/tracking/1_tracking_raw.csv
outputs/top/tracking/2_tracking_raw.csv

Expected SHA256:
1_tracking_raw.csv =
9fa203913d994ca0b25658c6d4d88ddd1d0d46e0b3e19a9ce7a06732e144373f

2_tracking_raw.csv =
500323ccb3d928c2f8953e90321877d93c1562cef8b1c627dc845f2048c764f6

N14 tracking:
PASS_WITH_WARNING

Trajectory usable:
YES

Important identity limitation:
1.mp4 has 33 unique tracker IDs with median 2 active tracks/frame.
2.mp4 has 53 unique tracker IDs with median 3 active tracks/frame.
Track ID is NOT biological identity.

TASK ORDER

1. Audit Git status and preserve all unrelated local modifications.
2. Read all required project/reference files.
3. Verify the two raw tracking files exist.
4. Verify their SHA256 hashes against N14 committed evidence.
5. Inspect the ACTUAL raw CSV schemas; do not guess column names.
6. Prepare Notebook 15 with:
   - TOP trajectory segmentation;
   - <=3-frame short-gap interpolation within SAME track ID only;
   - centered 5-frame rolling-median cleaning;
   - trajectory QC;
   - step-level 2D movement descriptors;
   - global synchronized 5-second windows with 1-second step;
   - individual movement/turning/spatial features;
   - observed-only instantaneous group/social descriptors;
   - nearest-neighbor distance;
   - pairwise distances;
   - group centroid;
   - group RMS radius / spatial spread;
   - bounding-area and convex-hull area where mathematically valid;
   - group polarization when >=2 valid headings;
   - individual and group feature QC;
   - schema JSON;
   - reproducibility logs and small research summaries.
7. Static-review Notebook 15.
8. Report exactly what the user needs to run.
9. STOP.

NON-NEGOTIABLE SCIENTIFIC RULES

Do NOT rerun YOLO training, validation, video detection, or ByteTrack.

Do NOT tune B30/B60/BoT-SORT.

Do NOT stitch different tracker IDs under any heuristic.

Do NOT infer cross-video or FRONT↔TOP biological identity.

Do NOT use interpolated positions as observed fish presence in PRIMARY group metrics.

Do NOT call n_active_tracks a fish count.

Do NOT output cm, cm/s, m or m/s.

Do NOT call image-frame edges tank walls. Tank geometry is not calibrated.

Use frame-relative continuous spatial metrics. Optional frame edge/center ratios must be named explicitly as frame-relative.

Set ARENA_GEOMETRY=None by default. Do not automatically infer a tank boundary.

Do NOT infer T1/T2 from 1.mp4 / 2.mp4.

Do NOT assign behavior labels such as NORMAL, FEEDING, STRESS, SICK, ANXIOUS, AGGRESSIVE.

Notebook 15 computes quantitative descriptors only.

WINDOW DESIGN

Use:
WINDOW_SEC = 5.0
STEP_SEC = 1.0
MIN_WINDOW_COVERAGE = 0.60
MAX_INTERP_GAP_FRAMES = 3
SMOOTH_WINDOW_FRAMES = 5

Use a GLOBAL per-video time grid:
[0,5), [1,6), [2,7), ...

Individual and group feature windows must share:
video_id
source_video
window_start_sec
window_end_sec
window_mid_sec

This is required for future Notebook 16 sensor synchronization.

PRIMARY OUTPUT POLICY

Full local outputs:
outputs/top/trajectory/
outputs/top/behavior/

Small committable evidence:
results/trajectory/
results/behavior/
logs/trajectory/TOP_TRAJECTORY_CLEANING_001/
logs/behavior/TOP_BEHAVIOR_FEATURES_001/

Do not put a large full trajectory table in results/.

Do not commit or stage anything in this preparation task.

NOTEBOOK EXECUTION POLICY

I will execute Notebook 15 manually in VS Code using the fish kernel.

You MUST NOT execute the notebook.

Do not use nbconvert --execute or papermill.

Do not fabricate code-cell outputs.

When Notebook 15 is ready, return:

REPOSITORY
Branch:
HEAD:
Working tree:

N14 INPUT PROVENANCE
Raw file paths:
SHA256 results:
Schema summary:

NOTEBOOK 15
Path:
Cells:
Kernel:
Static validation:

DESIGN
Trajectory cleaning:
Individual features:
Group features:
Identity handling:
Geometry handling:
Windowing:

FILES CREATED/MODIFIED
...

USER ACTION
Open notebooks/15_top_behavior_features.ipynb
Select fish kernel
Run manually

Status:
READY FOR USER RUN

Then STOP.

```
