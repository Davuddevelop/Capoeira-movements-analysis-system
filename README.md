# 🥋 Capoeira Vision — Movement Analysis System

> Real-time AI-powered pose detection and movement scoring for the **Azerbaijan Capoeira Federation**

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Tasks%20API-orange?style=flat-square)
![Vite](https://img.shields.io/badge/Vite-5.x-purple?style=flat-square&logo=vite)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎥 **Video Upload Analysis** | Upload a training video and get per-movement scores |
| 📷 **Live Camera Mode** | Real-time skeleton overlay via your webcam |
| 🦴 **Skeleton Overlay** | MediaPipe 33-point pose landmarks drawn on video |
| 📊 **Movement Scoring** | AI scores each Capoeira technique on a 0–10 scale |
| 📋 **Detailed Feedback** | Color-coded ✅ good / ❌ bad points per movement |
| 🎯 **Movement Selector** | Choose only the movements in your video before analysis |
| 📈 **Performance Chart** | Technique score & stability trend per session |

---

## 🏗️ Architecture

```
capoeira-movements-analysis-system/
├── capoeira-analyzer/          # Python FastAPI backend
│   ├── api.py                  # REST API endpoints
│   ├── analyzer/
│   │   ├── pose_detector.py    # MediaPipe Tasks API (Python 3.12 ✅)
│   │   ├── angle_calculator.py # Joint angle computation
│   │   └── report_generator.py # Session results
│   ├── movements/              # Per-movement scorers
│   │   ├── ginga.py
│   │   ├── au.py
│   │   ├── meia_lua.py
│   │   ├── armada.py
│   │   └── bencao.py
│   └── models/
│       └── pose_landmarker.task  # MediaPipe lite model
│
└── capoeira-dashboard/         # Vite + Vanilla JS frontend
    ├── index.html
    ├── src/
    │   ├── main.js             # UI logic, upload, MediaPipe JS
    │   └── style.css           # Glassmorphism dark theme
    └── vite.config.js          # Dev server + API proxy
```

---

## 🚀 Getting Started

### Prerequisites
- Python **3.12**
- Node.js **18+**

---

### 1. Backend — Python API

```bash
cd capoeira-analyzer

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install fastapi uvicorn mediapipe opencv-python numpy pandas

# Download MediaPipe pose model
python -c "
import urllib.request, pathlib
pathlib.Path('analyzer/models').mkdir(parents=True, exist_ok=True)
urllib.request.urlretrieve(
  'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task',
  'analyzer/models/pose_landmarker.task'
)
print('Model downloaded ✅')
"

# Start the API server
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

API will be live at **http://localhost:8000**

---

### 2. Frontend — Dashboard

```bash
cd capoeira-dashboard

npm install
npx vite --port 5174 --host
```

Dashboard will open at **http://localhost:5174**

---

## 🎬 How to Use

### Analyzing a Video
1. Click **"Analyze New Video"** in the top-right
2. Select your video file — it **instantly plays in the dashboard**
3. A movement selector appears — **check only the movements in your video**
4. Click **▶ Start Analysis**
5. Watch the progress bar while MediaPipe processes every frame
6. Results appear: scores, chart, and detailed ✅/❌ feedback per movement

### Live Camera
1. Click the **📷 Live Camera** button on the video panel
2. Allow camera permissions in your browser
3. The green skeleton will appear on your body in real time
4. Click **⏹ Stop Camera** to end the session

---

## 🥋 Supported Movements

| Movement | Description |
|---|---|
| **Ginga** | Side-to-side base movement — the heart of Capoeira |
| **Au (Cartwheel)** | Sideways handstand / cartwheel |
| **Meia-lua de Frente** | Half-moon front kick |
| **Armada** | Spinning back kick |
| **Bênção** | Front push kick |

---

## 🔌 API Reference

### `POST /analyze`

Analyze a video file for selected Capoeira movements.

**Form fields:**

| Field | Type | Description |
|---|---|---|
| `file` | `video/*` | The video file to analyze |
| `athlete_name` | `string` | Athlete display name |
| `movements` | `string` | Comma-separated movement names |

**Response:**
```json
{
  "athlete_name": "Davud A.",
  "session_id": "SESSION-A1B2C3D4",
  "overall_score": 7.4,
  "detection_stats": {
    "detected_frames": 412,
    "total_frames": 450,
    "detection_rate": 91.5
  },
  "movements": [
    {
      "movement_name": "Au (Cartwheel)",
      "overall_score": 7.4,
      "peak_score": 9.1,
      "average_score": 6.8,
      "feedback": ["Good arm extension detected", "Knee bend too shallow at peak"]
    }
  ]
}
```

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
- [MediaPipe Tasks API](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) — Pose landmark detection
- [OpenCV](https://opencv.org/) — Video frame extraction
- [NumPy](https://numpy.org/) — Joint angle mathematics

**Frontend**
- [Vite](https://vitejs.dev/) — Build tool & dev server
- [MediaPipe Tasks Vision JS](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/web_js) — Client-side real-time pose detection
- [Chart.js](https://www.chartjs.org/) — Performance charts
- Vanilla JS + CSS (Glassmorphism dark theme)

---

## 📸 Screenshots

> Dashboard with live skeleton overlay and movement breakdown

*Azerbaijan Capoeira Federation · Built with ❤️ and MediaPipe*