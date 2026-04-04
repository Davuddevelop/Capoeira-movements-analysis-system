"""
Capoeira Movement Analysis System - REST API

This API exposes the movement analysis logic to the modern web dashboard.
Run with: uvicorn api:app --reload

Project by: Azerbaijan Capoeira Federation
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import shutil
from pathlib import Path
from typing import List, Optional

# Import core analyzer components
from analyzer.pose_detector import PoseDetector, get_detection_stats
from analyzer.angle_calculator import AngleCalculator
from analyzer.report_generator import MovementResult
from movements import (
    GingaScorer, AuScorer, MeiaLuaScorer, ArmadaScorer, BencaoScorer
)

app = FastAPI(title="Capoeira Movement Analysis API")

# Enable CORS for the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AVAILABLE_MOVEMENTS = {
    'Ginga': GingaScorer,
    'Au (Cartwheel)': AuScorer,
    'Meia-lua de Frente': MeiaLuaScorer,
    'Armada': ArmadaScorer,
    'Bênção': BencaoScorer,
}

@app.get("/")
async def root():
    return {"message": "Capoeira Movement Analysis API is running", "version": "1.0.0"}

@app.post("/analyze")
async def analyze_video(
    athlete_name: str = Form(...),
    movements: Optional[str] = Form(None), # Comma separated list
    file: UploadFile = File(...)
):
    """
    Upload a video and analyze selected capoeira movements.
    """
    # Create temporary file for processing
    # Using a suffix that matches the uploaded file
    suffix = Path(file.filename).suffix
    fd, video_path = tempfile.mkstemp(suffix=suffix)
    
    try:
        with os.fdopen(fd, 'wb') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            
        # The file is now closed and can be safely opened by cv2 on Windows
        
        # Initialize components
        pose_detector = PoseDetector(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        angle_calculator = AngleCalculator(min_visibility=0.5)

        # Parse movements
        selected_movement_names = movements.split(',') if movements else ['Ginga']
        
        # Get video info
        video_info = pose_detector.get_video_info(video_path)

        all_angles = []
        frame_results = []
        timestamps = []

        # Process frames
        for result in pose_detector.process_video(video_path, draw_skeleton=False):
            frame_results.append(result)
            if result.pose_detected and result.landmarks:
                angles = angle_calculator.calculate_all_angles(result.landmarks.landmark)
                all_angles.append(angles)
                timestamps.append(result.timestamp)
            else:
                all_angles.append({})

        # Detection stats
        stats = get_detection_stats(frame_results)

        # Score selected movements
        results = []
        for name in selected_movement_names:
            name = name.strip()
            if name not in AVAILABLE_MOVEMENTS:
                continue
                
            scorer_class = AVAILABLE_MOVEMENTS[name]
            scorer = scorer_class()

            valid_angles = [a for a in all_angles if a]
            valid_timestamps = timestamps[:len(valid_angles)]
            
            movement_score = scorer.score_sequence(valid_angles, valid_timestamps)

            # Build result dictionary
            res = {
                "movement_name": scorer.movement_name,
                "overall_score": float(movement_score.overall_score),
                "peak_score": float(movement_score.peak_score),
                "average_score": float(movement_score.average_score),
                "feedback": movement_score.feedback_summary,
                "frame_scores": [float(fs.overall_score) for fs in movement_score.frame_scores]
            }
            results.append(res)

        # Overall session score
        overall_session_score = sum(r["overall_score"] for r in results) / len(results) if results else 0

        return {
            "athlete_name": athlete_name,
            "session_id": f"SESSION-{os.urandom(4).hex().upper()}",
            "video_metadata": {
                "filename": file.filename,
                "resolution": f"{video_info.width}x{video_info.height}",
                "fps": video_info.fps,
                "duration": video_info.duration,
                "total_frames": video_info.total_frames
            },
            "detection_stats": {
                "detected_frames": stats['detected_frames'],
                "total_frames": stats['total_frames'],
                "detection_rate": stats['detection_percentage']
            },
            "overall_score": round(overall_session_score, 1),
            "movements": results
        }

    except Exception as e:
        import traceback
        with open("error.log", "a") as f:
            f.write(f"\n--- ERROR at {os.urandom(4).hex()} ---\n")
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up
        if os.path.exists(video_path):
            os.remove(video_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
