# F1 Race Prediction

A machine learning system that predicts top-3 finish probabilities for Formula 1 races using qualifying data, practice session metrics, historical driver form, and weather conditions.

---

## Overview

Before each race weekend, after qualifying ends, this system:

1. Pulls live F1 data via the [FastF1](https://github.com/theOehrly/Fast-F1) library
2. Engineers 26 features per driver (qualifying pace, practice runs, weather, reliability, etc.)
3. Trains and runs three calibrated ML models in parallel
4. Serves an interactive dashboard showing predicted top-3 probabilities with feature-level explanations

After the race, actual results are loaded and model accuracy is evaluated.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10, Flask |
| ML | scikit-learn, XGBoost |
| F1 Data | FastF1 3.x |
| Frontend | Vanilla HTML/JS (dark F1-themed dashboard) |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/kapilpandya22/f1-race-prediction.git
cd f1-race-prediction

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the App

### Option 1 — Windows Quick Start

Double-click `start.bat`. It starts the Flask server and opens the dashboard in your browser automatically.

### Option 2 — Manual

```bash
python app.py
```

The server starts on **`http://localhost:5000`**.

---

## Accessing the Frontend

| URL | Page |
|---|---|
| `http://localhost:5000` | Landing page |
| `http://localhost:5000/dashboard` | Main prediction dashboard |

The dashboard lets you:

- Select an F1 race from the 2026 calendar (22 races)
- Choose a model: **Logistic Regression**, **Random Forest**, or **XGBoost**
- Click **Analyze** to trigger the prediction pipeline (progress streams in real time)
- View predicted top-3 drivers with their probabilities
- Inspect feature importance and per-driver contribution breakdowns
- After the race, run metrics to see how accurate the prediction was

Race status is color-coded:

| Color | Meaning |
|---|---|
| Gray | Data not yet available (before qualifying) |
| Cyan | Prediction available |
| Green | Race completed — metrics evaluated |

---

## Backend API

The Flask server exposes the following endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/races/status` | GET | All 22 races with their prediction status |
| `/api/data` | GET | Predictions, feature importance, driver explanations, and metrics for a race |
| `/api/update` | POST | Trigger prediction pipeline (streams SSE progress) |
| `/api/run/metrics` | POST | Evaluate model accuracy after the race finishes |

### Example — Trigger Predictions

```bash
curl -X POST http://localhost:5000/api/update \
  -H "Content-Type: application/json" \
  -d '{"model": "random_forest"}'
```

### Example — Run Metrics After Race

```bash
curl -X POST http://localhost:5000/api/run/metrics \
  -H "Content-Type: application/json" \
  -d '{"race": "Australian Grand Prix"}'
```

---

## ML Models

All three models are trained on the same 26-feature dataset (2023–2025 seasons) with recent races weighted higher. Each model is wrapped in `CalibratedClassifierCV` to produce reliable probability scores.

| Model | Notes |
|---|---|
| Logistic Regression | L2 regularization, class-balanced |
| Random Forest | 400 trees, depth 10 |
| XGBoost | 300 estimators, learning rate 0.05 |

**Target:** Binary — does a driver finish in the Top 3?

### Feature Categories

- **Qualifying:** grid position, gap to pole, Q-stage reached
- **Practice:** long-run pace, consistency
- **Driver form:** average finish over last 5 races
- **Constructor:** team championship position, points per race, teammate gap
- **Track:** circuit type (permanent vs. street), overtaking difficulty
- **Weather:** rain probability, wet flag, temperature, humidity, wind speed
- **Interaction terms:** quali × pace, form × quali, rain × quali
- **Reliability:** historical DNF rate

### Evaluation Metrics

After each race the system computes: Accuracy, F1, ROC AUC, Brier Score, MRR, Top-3 Accuracy, Top-3 Precision, Top-3 Recall.

---

## Prediction Workflow

```
Qualifying ends
      │
      ▼
POST /api/update  ──►  FastF1 fetches data
                        │
                        ▼
                   Feature engineering (26 features per driver)
                        │
                        ▼
                   Train + run 3 models
                        │
                        ▼
                   outputs/predictions/{model}/{race}/
                   ├── predictions.csv
                   ├── predictions_with_features.csv
                   └── feature_importance.csv

Race finishes
      │
      ▼
POST /api/run/metrics  ──►  Load official results
                             │
                             ▼
                        Evaluate against ground truth
                             │
                             ▼
                        metrics.json  (accuracy, AUC, etc.)
```

---

## Project Structure

```
f1-race-prediction/
├── app.py                  # Flask server (entry point)
├── start.bat               # Windows one-click launcher
├── requirements.txt
├── config/
│   └── config.yaml
├── dashboards/             # Frontend HTML + assets
│   ├── f1_step1_v9.html    # Landing page
│   ├── f1_dashboard_p2.html
│   └── f1_bg.mp4
├── data/
│   ├── calendar.py         # F1 race schedules (2023–2026)
│   ├── load_data.py        # FastF1 data fetching
│   ├── process_data.py
│   ├── raw/                # Raw CSV data
│   ├── processed/          # Feature-ready CSVs
│   └── golden/             # Official race results
├── features/               # Feature engineering pipeline
├── models/                 # logistic.py, random_forest.py, xgboost.py
├── pipelines/              # run_prediction.py, run_metrics.py
├── evaluation/             # Metrics and benchmarking
├── explainability/         # Feature importance and driver explanations
└── outputs/
    ├── predictions/        # Per-race predictions (by model)
    └── analysis/           # Evaluation results (by model)
```

---

## Notes

- `data/cache/` is excluded from git (FastF1 cache can exceed 3 GB). It is auto-created on first run.
- No database is used — all outputs are stored as CSV/JSON files under `outputs/`.
- The system currently targets the **2026 F1 season** (22 races).
