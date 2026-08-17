# AGENTS.md — Fish AI Research Project

## 1. Source of truth

Always read and follow:

`FISH_AI_PROJECT_WORKFLOW.md`

This file is the authoritative workflow for the project and defines:
- experiment order;
- notebook order;
- repository structure;
- data-management rules;
- evidence/logging requirements;
- scientific constraints.

If there is a conflict between an ad-hoc implementation idea and the workflow, follow `FISH_AI_PROJECT_WORKFLOW.md` unless the user explicitly instructs otherwise.

---

## 2. Sequential execution

Work on only **one notebook / one experimental step at a time**.

Default order:

`00 → 01 → 02 → ... → 19`

After completing one notebook or experimental step:

1. for Notebook 01 onward, prepare it and stop for the user to run it manually in VS Code as required by Section 8; Notebook 00 is the completed historical exception;
2. verify outputs;
3. save logs;
4. save summary/results;
5. report files changed/created;
6. report errors or warnings;
7. state the next proposed step;
8. **STOP and wait for user approval.**

Do not automatically continue to the next notebook even if the current step succeeds.

---

## 3. Authentication and login rule

All login, OAuth, account authorization, device-code authorization, API-key setup, token creation, password entry, credential-file creation, or secret management must be performed manually by the user.

This applies to, but is not limited to:

- GitHub;
- Google Drive;
- rclone;
- Roboflow;
- Hugging Face;
- cloud services;
- external APIs.

If authentication is required:

1. STOP the current workflow;
2. clearly state which service requires authentication;
3. explain why authentication is needed;
4. give the exact command or manual steps the user should perform;
5. tell the user what successful output/state to look for;
6. wait for the user to confirm completion;
7. only then perform a read-only status check and continue.

Never:
- enter credentials for the user;
- generate account secrets for the user;
- copy passwords/tokens into notebooks;
- store secrets in the repository;
- commit secret-bearing files;
- automatically initiate OAuth flows if manual user interaction is required;
- silently modify credential configuration.

If a service is already authenticated, only perform non-destructive status checks unless the user explicitly asks for a credential change.

---

## 4. Git and GitHub policy

GitHub is used for research provenance and project management.

Commit:
- notebooks;
- source code;
- scripts;
- configs;
- documentation;
- environment manifests;
- logs;
- small CSV/JSON summaries;
- small plots used as research evidence.

Do not commit:
- raw videos;
- downloaded Google Drive datasets;
- full Roboflow datasets;
- model weights such as `.pt`;
- large binary model files;
- training caches;
- overlay videos;
- large processed datasets;
- large Parquet files;
- credentials;
- secrets.

Before staging files:
1. inspect `.gitignore`;
2. inspect `git status`;
3. ensure no large data or secrets are being staged.

Do not use destructive Git operations unless the user explicitly asks:
- `git reset --hard`;
- force push;
- destructive rebase;
- branch deletion;
- history rewriting.

Do not automatically push to GitHub if authentication has not been confirmed by the user.

---

## 5. Data policy

Source-of-truth:

### Google Drive
Stores:
- raw videos;
- raw sensor data;
- original experiment data;
- final model archive if needed.

### Roboflow
Stores:
- labeled detection images;
- dataset versions;
- train/validation/test splits.

### Local WSL
Stores temporary working copies such as:
- `data/raw/`
- `data/roboflow/`
- `data/processed/`
- `data/eval/`
- `models/`
- `runs/`
- `outputs/`
- `artifacts_local/`

Local heavy data is disposable after:
- source data is confirmed on Drive/Roboflow;
- final model is archived;
- research evidence is committed/pushed.

Never delete or modify remote source data unless the user explicitly requests it.

---

## 6. Path policy

Use repository-relative paths.

Do not hard-code paths from previous machines such as:

`/home/diy-hus/fish/...`

Resolve project root programmatically.

Preferred pattern:

```python
from pathlib import Path

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name == "notebooks":
    PROJECT_ROOT = PROJECT_ROOT.parent
```

Centralize paths in:

`configs/paths.yaml`

A machine change should require minimal or no notebook edits.

---

## 7. Python and Conda environment

Primary Conda environment:

`fish`

Before running research code:
1. confirm active environment;
2. confirm Python interpreter;
3. confirm Jupyter kernel points to the same environment;
4. record package versions.

Do not create a new environment unless the user explicitly approves.

Do not perform broad upgrades such as:

`pip install -U ...`

unless clearly necessary.

If a package is missing:
1. identify the minimum required package;
2. check likely dependency conflicts;
3. explain the change;
4. install only what is required;
5. log the environment change.

Record environment using:

```bash
conda env export --from-history > environment/environment.yml
pip freeze > environment/pip_freeze.txt
```

---

## 8. Notebook policy

Notebook is the main experimental unit.

Every experimental notebook should contain:

1. title;
2. scientific/technical objective;
3. CONFIG section;
4. input validation;
5. reproducible execution cells;
6. metrics;
7. output paths;
8. summary;
9. conclusion / decision;
10. next step.

Notebook names and order follow `FISH_AI_PROJECT_WORKFLOW.md`.

Do not:
- embed secrets;
- hard-code old machine paths;
- print huge DataFrames;
- embed large videos;
- store large binary objects inside notebooks;
- silently mutate unrelated project state.

For large outputs:
- save full data locally;
- keep only summaries in notebook;
- copy small summary files to `results/`.

### 8.1. Notebook execution ownership

From Notebook 01 onward, every notebook must be executed directly by the user with **Run** or **Run All** in VS Code.

Codex must not automatically execute notebooks.

Codex must not use:
- `jupyter nbconvert --execute`;
- `jupyter execute`;
- Papermill;
- nbclient to execute a notebook;
- a Python script to automatically run an entire notebook;
- a terminal or background process to run a notebook for the user.

Codex may only:
1. create a notebook;
2. edit a notebook;
3. perform static code inspection;
4. check syntax when possible without running an experiment;
5. prepare the CONFIG section;
6. explain which cells the user must run;
7. identify expected inputs and outputs;
8. stop so the user can open the notebook in VS Code and select **Run** or **Run All**.

After preparing a notebook, Codex must report exactly:

> Notebook đã sẵn sàng để chạy thủ công trong VS Code.
> Hãy mở `<notebook path>`, chọn kernel fish và bấm Run All.
> Sau khi chạy xong, Save notebook và báo tôi để kiểm tra kết quả.

### 8.2. Notebook logging requirements

Because the user directly observes notebook execution, every notebook must display clear logs in cell outputs.

Every notebook must include:

1. An initial cell that displays:
   - experiment ID;
   - datetime;
   - `PROJECT_ROOT`;
   - Python executable;
   - Conda environment;
   - device;
   - GPU, if available.
2. A CONFIG cell that prints all important configuration before the experiment starts.
3. Progress logs for long-running steps. For video processing, include:
   - total frame count;
   - source FPS;
   - resolution;
   - progress every 100 or 200 frames;
   - elapsed time;
   - processing FPS.
   Do not emit excessive per-frame logs.
4. When creating a file, print:
   - output path;
   - number of records or frames;
   - file size when useful.
5. A final cell that displays:
   - `PASS`, `PASS_WITH_WARNING`, or `FAIL`;
   - runtime;
   - main metrics;
   - output files;
   - warnings;
   - next step.
6. Unhidden tracebacks. If a cell fails, its error must remain directly visible in the notebook so the user can inspect it.

### 8.3. User run gate

The mandatory workflow for every notebook from Notebook 01 onward is:

**Codex:**
- prepare the notebook;
- perform static checks only;
- report that the notebook is ready;
- stop.

**User:**
- open the notebook in VS Code;
- verify that the kernel is `fish`;
- select **Run All**;
- observe the logs;
- save the notebook;
- send the result to Codex.

**Codex:**
- read the saved results;
- analyze metrics and logs;
- edit the notebook if necessary;
- stop again so the user can rerun it manually.

Codex may prepare the next notebook only after the user explicitly confirms that the current notebook passed.

### 8.4. Authentication in notebooks

All existing authentication and login rules remain in force.

If a notebook requires Google Drive authentication, rclone OAuth, Roboflow API authentication, GitHub login, a token, or a credential, Codex must stop before that step and the user must perform authentication manually.

Avoid putting authentication in notebook cells whenever possible.

Research notebooks must never contain:
- passwords;
- API keys;
- access tokens;
- OAuth tokens;
- credentials.

### 8.5. Notebook 00 exception

Notebook 00 was completed and executed before the notebook execution ownership rule was introduced. Do not change the Checkpoint 00 result.

Mandatory user-manual execution applies from Notebook 01 onward.

---

## 9. Experiment provenance

Every meaningful experiment should have an `experiment_id`.

Minimum provenance:

- experiment_id;
- date/time;
- purpose;
- inputs;
- source video/dataset;
- dataset version;
- model;
- model SHA-256 when applicable;
- parameters/configuration;
- random seed when applicable;
- Python version;
- package versions;
- hardware/GPU;
- runtime;
- metrics;
- output paths;
- Git commit when available;
- notes.

Preferred research evidence structure:

```text
logs/<stage>/<experiment_id>/
├── config.yaml
├── environment.txt
├── summary.json
└── stdout.log
```

Copy small comparative results to:

`results/`

The target provenance chain is:

```text
paper result
↓
results file
↓
experiment_id
↓
logs
↓
notebook/script
↓
git commit
↓
source data / dataset version / model hash
```

---

## 10. Experimental discipline

For ablation studies:
- change one main variable at a time;
- hold other settings constant;
- do not tune by visual preference only;
- preserve previous outputs;
- do not overwrite baselines;
- label each run clearly.

Do not select a configuration because the overlay merely “looks better”.

Use quantitative metrics and predefined decision criteria.

---

## 11. Scientific constraints

Do not call a diagnostic metric “accuracy” unless appropriate ground truth exists.

Do not conclude a fish is:
- stressed;
- sick;
- healthy;
- happy;

unless there is a scientifically defensible ground truth or validation protocol.

Do not assume:
- `track_id` is permanent biological identity;
- Front ID equals Top ID;
- a long nominal lifespan means a continuous valid trajectory;
- count agreement implies correct identity association.

Avoid data leakage:
- do not train on test video;
- do not use evaluation frames for model tuning unless they are explicitly reclassified as training data and a new independent test set is created;
- preserve independent evaluation data.

---

## 12. Detection workflow rules

Detection must be validated before tracking.

Keep evidence for:
- dataset audit;
- training;
- validation;
- video inference;
- confidence ablation;
- failure analysis.

For known fish count videos, count diagnostics may include:
- mean detections/frame;
- exact-count rate;
- undercount rate;
- overcount rate;
- count MAE;
- count RMSE;
- count bias.

These are diagnostic count metrics, not substitutes for bbox Precision/Recall/mAP unless ground-truth boxes exist.

---

## 13. Tracking workflow rules

Tracking follows detection validation.

For tracker comparisons, preserve:
- same detector;
- same model;
- same video;
- same detection thresholds unless the experiment explicitly studies them.

Useful diagnostic metrics:
- unique track IDs;
- proliferation factor;
- median/mean/longest lifespan;
- IDs ≤1 s;
- IDs ≤2 s;
- IDs ≥5 s;
- IDs ≥10 s;
- gaps;
- missing frames inside lifespan;
- count metrics;
- processing FPS.

Do not call these official MOT accuracy metrics.

Official MOT evaluation requires ground-truth identity and may include:
- HOTA;
- IDF1;
- ID switches;
- fragmentation.

---

## 14. Behavior workflow rules

Do not begin behavior classification until tracking quality is sufficient for the intended temporal window.

Front-camera initial observable descriptors may include:
- speed;
- path length;
- vertical position;
- vertical velocity;
- vertical range;
- surface/middle/bottom ratios;
- stop duration;
- burst frequency.

Initial labels should remain observational, for example:
- low_activity;
- normal_activity;
- rapid_activity;
- surface;
- middle;
- bottom;
- upward;
- downward;
- vertical_stable.

Behavior windows should be explicitly defined and documented.

---

## 15. Top-camera and multi-camera rule

Develop Top independently first.

Do not assume:
`Front track_id == Top track_id`

Synchronize cameras by time before attempting identity fusion.

Cross-camera identity is a separate research problem and must not be silently assumed.

---

## 16. Sensor-data rule

Sensor synchronization must use timestamps.

Keep raw sensor data unchanged.

Any cleaned/interpolated sensor dataset must:
- be saved separately;
- document the transformation;
- retain reference to the raw source.

---

## 17. Error-handling rule

When an error occurs:

1. read the full traceback/log;
2. identify the likely root cause;
3. make the smallest justified change;
4. rerun only the necessary step;
5. record the change.

Do not:
- hide errors with broad `try/except`;
- ignore corrupted data;
- randomly upgrade/downgrade major frameworks;
- modify multiple unrelated settings at once.

If a fix might damage the environment, data, repository history, or remote resources:
**STOP and ask the user.**

---

## 18. External download rule

For Drive/Roboflow data:
- download to local ignored directories;
- never treat local copies as the only archive;
- log source/version/date/path;
- avoid unnecessary duplicate copies.

If login is required, follow the authentication rule and stop for user action.

---

## 19. Cleanup rule

Never delete heavy local data automatically just because it appears reproducible.

Before proposing deletion, verify:
- raw data exists on Drive;
- Roboflow dataset version still exists;
- final models are backed up;
- notebooks/logs/results/configs are committed;
- checksums/manifests are saved.

Deletion must be a separate user-approved step.

---

## 20. Current-machine rebuild rule

On a newly installed machine, follow this order:

1. inspect repository;
2. verify `fish` Conda env;
3. run Notebook 00 environment check;
4. validate relative paths;
5. restore a small amount of data;
6. verify video reading;
7. restore Roboflow dataset;
8. reproduce detector validation;
9. reproduce video detection;
10. only then reproduce tracking;
11. only after tracking evaluation continue to behavior.

Do not skip directly to later experiments simply because old results exist.

Old results are reference baselines until reproduced on the new machine.

---

## 21. Stop points requiring user approval

Always stop for user confirmation before:
- moving to the next notebook;
- performing login/authentication;
- installing a major dependency;
- changing Conda environment structure;
- modifying remote Drive/Roboflow data;
- changing train/validation/test split;
- retraining a model when not already approved;
- deleting local data;
- pushing to GitHub for the first time in a new setup if auth/state is uncertain;
- using destructive Git commands;
- starting behavior classification after tracking;
- starting Raspberry Pi deployment.

---

## 22. Default completion report for each step

At the end of each notebook/step, report:

### Completed
- notebook/script executed;
- purpose;
- inputs;
- configuration.

### Outputs
- files created;
- files modified;
- logs;
- summaries.

### Results
- key metrics;
- warnings;
- anomalies.

### Reproducibility
- environment;
- model hash if applicable;
- dataset version;
- Git status/commit if applicable.

### Decision
- whether the step passed its intended checkpoint;
- recommended next notebook.

Then:

**STOP and wait for user approval.**

---

## 23. First action when opening this repository

Before modifying anything:

1. read `AGENTS.md`;
2. read `FISH_AI_PROJECT_WORKFLOW.md`;
3. inspect repository structure;
4. inspect Git status;
5. identify current Conda environment;
6. identify Python interpreter;
7. identify existing notebooks/logs/results;
8. report gaps versus the workflow.

Do not modify files until the user approves the proposed first step.
