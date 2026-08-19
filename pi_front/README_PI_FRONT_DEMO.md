# Front Fish AI Demo — Raspberry Pi 4 + Google Coral USB Edge TPU

## Scope

This is the **Front-camera-only** deployment demo derived from Notebooks 10–13.

Runtime pipeline:

`Front frame -> YOLO detector on Coral Edge TPU -> ByteTrack -> trajectory cleaning -> 5 s / 1 s behavior features -> 4-class Random Forest -> demo UI`

The 4 behavior classes are:

- `NORMAL_SWIM`
- `PAIR_INTERACTION`
- `SHELTER_TRANSITION`
- `FEEDING`

`LOW_ACTIVITY` is not a model class because the current manually labeled GT contains no confirmed samples for it.

The software deliberately displays distance in **pixels** and speed in **pixels/second**. Do not call these cm or cm/s until camera/tank calibration is completed.

Track ID is the tracker's identity and is **not guaranteed to be a biological individual identity**.

---

## Files to copy from the research project

Keep the exact research artifacts:

```text
runs/front/yolov8n_front_v1_baseline/weights/best.pt
configs/trackers/front_bytetrack_b15.yaml
models/behavior/front_behavior_model.joblib
models/behavior/front_behavior_model_metadata.json
results/behavior/front_behavior_feature_schema.json
```

You do **not** run the `.pt` detector on the Coral. First export it on the x86_64 research computer.

---

## Step A — export the Front detector on the x86_64 research computer

Run from the research project root, using the existing `fish` environment.

Example:

```bash
conda activate fish

python deploy/pi_front/export_front_edgetpu.py \
  --imgsz 512 \
  --data datasets/front/detect_v1/data.yaml
```

If your actual `data.yaml` is elsewhere, pass the real path.

The resulting filename must keep the suffix:

```text
*_edgetpu.tflite
```

Do not export on the Raspberry Pi. Edge TPU compilation is an x86 task.

### Why start at 512?

For this project the detector was developed at higher resolution, and fish can occupy a small part of the frame. `512` is a reasonable first demo balance between resolution and Coral speed.

After the first demo, compare 320 versus 512 on the same fixed video before choosing the final Pi setting.

---

## Step B — recommended Pi folder

Example:

```text
/home/pi/fish_demo/
├── fish_monitor.py
├── models/
│   ├── <front_detector>_edgetpu.tflite
│   ├── front_behavior_model.joblib
│   └── front_behavior_model_metadata.json
├── results/
│   └── behavior/
│       └── front_behavior_feature_schema.json
├── configs/
│   └── trackers/
│       └── front_bytetrack_b15.yaml
└── demo/
    └── 3.mp4
```

Copy the exact selected ByteTrack B15 YAML from the research project. Do not silently replace it with another tracker configuration if you want the demo to stay consistent with the experiments.

---

## Step C — Pi environment

Target:

- Raspberry Pi 4
- Raspberry Pi OS Bookworm 64-bit Desktop
- Google Coral USB Accelerator in a **USB 3** port
- active cooling recommended

Use the current Edge TPU runtime installation method documented by Ultralytics for Raspberry Pi + Coral, then install/update `tflite-runtime`.

For the Python application you need:

```text
ultralytics
tflite-runtime
opencv
numpy
joblib
scikit-learn
```

The behavior model is a scikit-learn/joblib artifact. Prefer the same scikit-learn major/minor version used on the training computer.

---

## Step D — first demo with a prerecorded Front video

Run from `/home/pi/fish_demo`:

```bash
python fish_monitor.py \
  --source demo/3.mp4 \
  --det-model models/<front_detector>_edgetpu.tflite \
  --tracker configs/trackers/front_bytetrack_b15.yaml \
  --behavior-model models/front_behavior_model.joblib \
  --metadata models/front_behavior_model_metadata.json \
  --schema results/behavior/front_behavior_feature_schema.json \
  --fullscreen
```

For the first scientific demo, a prerecorded Front clip is preferable because you can compare Pi output against the same source used during development.

---

## Step E — live USB camera

```bash
python fish_monitor.py \
  --source 0 \
  --det-model models/<front_detector>_edgetpu.tflite \
  --tracker configs/trackers/front_bytetrack_b15.yaml \
  --behavior-model models/front_behavior_model.joblib \
  --metadata models/front_behavior_model_metadata.json \
  --schema results/behavior/front_behavior_feature_schema.json \
  --camera-width 1280 \
  --camera-height 720 \
  --camera-fps 30 \
  --fullscreen
```

If the camera is not exposed as an OpenCV/V4L2 device, camera capture should be adapted separately (for example Picamera2). Keep detector/tracker/behavior logic unchanged.

---

## Screen layout

Default display is `800x480`:

- ~65% left: Front video
  - bounding boxes
  - Track ID
  - detection confidence
  - 1-second cleaned trajectory tail
- ~35% right:
  - Coral status
  - neural-network inference ms
  - pipeline FPS
  - Track ID
  - distance last 1 s (px)
  - mean speed (px/s)
  - predicted 4-class behavior
  - behavior probability when available

The UI marks the behavior model as experimental because the current grouped-CV macro-F1 is moderate and `FEEDING` has only 7 GT windows.

---

## Controls

```text
q or ESC : quit
r        : start/stop recording
```

When recording is enabled, the program writes:

```text
outputs/pi_front_demo/<timestamp>/
├── front_demo_overlay.mp4
└── front_demo_telemetry.csv
```

---

## Suggested first acceptance test

Use one fixed Front video and record these values:

```text
1. Coral status = ACTIVE
2. NN inference ms
3. pipeline FPS
4. number of current Track IDs
5. visual bbox/trajectory stability
6. behavior output after the first 5 seconds
7. CPU temperature / throttling state
```

Do not use the Pi demo to claim higher scientific accuracy than Notebook 13. The demo tests **deployment feasibility and real-time behavior**, while Notebook 13 remains the source for classifier evaluation.
