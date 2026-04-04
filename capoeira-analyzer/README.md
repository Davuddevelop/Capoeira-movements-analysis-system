# Capoeira Movement Analysis System

An AI-powered tool that analyzes capoeira athlete performances using computer vision. This project is developed in collaboration with the **Azerbaijan Capoeira Federation**.

## Overview

This system uses Google MediaPipe Pose detection to analyze capoeira movements from video recordings. It calculates joint angles, scores movements based on predefined criteria, and generates detailed reports for athletes and coaches.

### Features

- **Video Analysis**: Process recorded video files of capoeira performances
- **Pose Detection**: Detect 33 body landmarks using MediaPipe Pose
- **Angle Calculation**: Calculate joint angles (knee, hip, elbow, shoulder, spine, ankle)
- **Movement Scoring**: Score specific capoeira movements (0-10 scale)
- **Visual Reports**: Generate HTML/Text reports with scores and feedback
- **Web Interface**: User-friendly Streamlit web application

### Supported Movements

1. **Ginga** - The fundamental capoeira movement
2. **Au** - Cartwheel
3. **Meia-lua de Frente** - Semicircular kick forward
4. **Armada** - Spinning kick
5. **Bênção** - Front push kick

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Webcam or video files for analysis

### Setup

1. Clone or download this repository:
```bash
cd capoeira-analyzer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

Launch the Streamlit web application:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

1. Enter the athlete's name
2. Select movements to analyze
3. Upload a video file
4. Click "Analyze Video"
5. View results and download reports

### Command Line Interface

Analyze a video:
```bash
python main.py analyze path/to/video.mp4 -n "Athlete Name" -m ginga
```

Options:
- `-n, --name`: Athlete name
- `-m, --movements`: Movements to analyze (ginga, au, meia_lua, armada, bencao)
- `-f, --format`: Output format (text or html)
- `--save-video`: Save annotated video with skeleton overlay
- `-q, --quiet`: Quiet mode

Show video information:
```bash
python main.py info path/to/video.mp4
```

List available movements:
```bash
python main.py movements
```

Run system tests:
```bash
python main.py test
```

## Project Structure

```
capoeira-analyzer/
├── main.py                  # CLI entry point
├── app.py                   # Streamlit web interface
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── analyzer/               # Core analysis modules
│   ├── __init__.py
│   ├── pose_detector.py    # MediaPipe pose detection
│   ├── angle_calculator.py # Joint angle calculations
│   ├── movement_scorer.py  # Base scoring class
│   └── report_generator.py # Report generation
│
├── movements/              # Movement-specific scorers
│   ├── __init__.py
│   ├── ginga.py           # Ginga criteria
│   ├── au.py              # Au (cartwheel) criteria
│   ├── meia_lua.py        # Meia-lua de frente criteria
│   ├── armada.py          # Armada criteria
│   └── bencao.py          # Bênção criteria
│
├── data/
│   └── sample_videos/     # Test videos
│
└── output/
    └── reports/           # Generated reports
```

## Important Notes

### Calibration Required

**All movement scoring criteria are currently using PLACEHOLDER values.**

The angle thresholds for scoring must be calibrated with:
- Elgiz teacher
- Azerbaijan Capoeira Federation

To calibrate a movement:
1. Record a video of correct technique (coach-approved)
2. Run the analysis to get angle measurements
3. Update the constants in the movement file (e.g., `movements/ginga.py`)
4. Test and adjust as needed

### How Scoring Works

Each movement is scored based on joint angles compared to ideal ranges:
- **10/10**: Angle within ideal range
- **7-9**: Close to ideal
- **5-6**: Noticeable deviation
- **0-4**: Significant correction needed

Score colors:
- 🟢 Green: 7-10 (Good to Excellent)
- 🟡 Yellow: 5-6 (Fair)
- 🔴 Red: 0-4 (Needs Work)

## Technical Details

### Pose Detection

Uses MediaPipe Pose which provides:
- 33 body landmarks per frame
- x, y, z coordinates plus visibility
- Works with various camera angles
- Real-time capable (Phase 2)

### Angle Calculation

Calculates angles using vector mathematics:
```python
angle = arctan2(c.y - b.y, c.x - b.x) - arctan2(a.y - b.y, a.x - b.x)
```

Where A, B, C are three points and B is the vertex.

### Report Generation

Reports include:
- Athlete information
- Video metadata
- Per-movement scores with feedback
- Frame-by-frame angle data (optional)
- Downloadable in text or HTML format

## Phase 2 (Future)

Not implemented yet:
- Real-time webcam analysis
- Multi-athlete comparison
- Progress tracking over time
- Mobile app version
- Federation database integration

## Troubleshooting

### Common Issues

1. **MediaPipe not detecting pose**
   - Ensure good lighting
   - Athlete should be fully visible
   - Try a different camera angle

2. **Low detection rate**
   - Increase video quality
   - Reduce fast movements
   - Ensure contrasting background

3. **Import errors**
   - Verify all dependencies installed
   - Check Python version (3.10+)
   - Run `python main.py test`

## Contributing

This project is developed for the Azerbaijan Capoeira Federation. Contact the federation for contribution guidelines.

## License

[To be determined by the Azerbaijan Capoeira Federation]

## Acknowledgments

- Azerbaijan Capoeira Federation
- Elgiz teacher
- Google MediaPipe team
- Streamlit team

---

**Version:** 1.0.0 (Phase 1)
**Contact:** Azerbaijan Capoeira Federation
