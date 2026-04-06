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
from analyzer.movement_detector import MovementDetector, MovementCategory
from analyzer.combination_analyzer import analyze_combination
from movements import (
    GingaScorer, AuScorer, MeiaLuaScorer, ArmadaScorer, BencaoScorer,
    QueixadaScorer, MarteloScorer, EsquivaScorer, NegativaScorer,
    AVAILABLE_SCORERS
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
    'Queixada': QueixadaScorer,
    'Martelo': MarteloScorer,
    'Esquiva': EsquivaScorer,
    'Negativa': NegativaScorer,
}

# Mapping from detector names to scorer keys
DETECTOR_TO_SCORER = {
    'ginga': 'Ginga',
    'ginga_baixa': 'Ginga',
    'armada': 'Armada',
    'meia_lua_de_frente': 'Meia-lua de Frente',
    'bencao': 'Bênção',
    'queixada': 'Queixada',
    'martelo': 'Martelo',
    'au': 'Au (Cartwheel)',
    'au_batido': 'Au (Cartwheel)',
    'au_fechado': 'Au (Cartwheel)',
    'au_sem_mao': 'Au (Cartwheel)',
    'esquiva_lateral': 'Esquiva',
    'esquiva_baixa': 'Esquiva',
    'cocorinha': 'Esquiva',
    'resistencia': 'Esquiva',
    'negativa': 'Negativa',
    'role': 'Negativa',
    'queda_de_quatro': 'Negativa',
    'bananeira': 'Au (Cartwheel)',
    'ponte': 'Au (Cartwheel)',
    'queda_de_rins': 'Au (Cartwheel)',
    'meia_lua_de_compasso': 'Meia-lua de Frente',
    'rabo_de_arraia': 'Meia-lua de Frente',
    'chapa': 'Bênção',
    'ponteira': 'Bênção',
    'pisao': 'Bênção',
    'gancho': 'Martelo',
    'chibata': 'Martelo',
    'joelhada': 'Bênção',
    'cotovelhada': 'Bênção',
    'cabecada': 'Bênção',
    'macaco': 'Au (Cartwheel)',
    's_dobrado': 'Au (Cartwheel)',
    'parafuso': 'Armada',
    'piao_de_mao': 'Au (Cartwheel)',
    'mortal': 'Au (Cartwheel)',
    'folha_seca': 'Au (Cartwheel)',
    'rasteira': 'Negativa',
    'banda': 'Negativa',
    'tesoura': 'Negativa',
    'vingativa': 'Negativa',
    'escorpiao': 'Martelo',
}


@app.get("/")
async def root():
    return {"message": "Capoeira Movement Analysis API is running", "version": "2.0.0"}


@app.post("/analyze")
async def analyze_video(
    athlete_name: str = Form(...),
    movements: Optional[str] = Form(None),  # Comma separated list (optional)
    auto_detect: Optional[str] = Form("true"),  # Enable automatic detection
    file: UploadFile = File(...)
):
    """
    Upload a video and analyze capoeira movements.

    With auto_detect=true (default), movements are detected automatically.
    Otherwise, provide a comma-separated list of movement names.
    """
    # Create temporary file for processing
    suffix = Path(file.filename).suffix
    fd, video_path = tempfile.mkstemp(suffix=suffix)

    try:
        with os.fdopen(fd, 'wb') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)

        # Initialize components
        pose_detector = PoseDetector(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        angle_calculator = AngleCalculator(min_visibility=0.5)
        movement_detector = MovementDetector(min_confidence=0.3)

        # Get video info
        video_info = pose_detector.get_video_info(video_path)

        all_angles = []
        frame_results = []
        timestamps = []
        frame_detections = []

        # Process frames
        for result in pose_detector.process_video(video_path, draw_skeleton=False):
            frame_results.append(result)
            if result.pose_detected and result.landmarks:
                angles = angle_calculator.calculate_all_angles(result.landmarks.landmark)
                all_angles.append(angles)
                timestamps.append(result.timestamp)

                # Auto-detect movement in this frame
                detection = movement_detector.detect(result.landmarks, angles)
                frame_detections.append(detection)
            else:
                all_angles.append({})
                frame_detections.append(None)

        # Detection stats
        stats = get_detection_stats(frame_results)

        # =================================================================
        # AUTO-DETECTED MOVEMENTS
        # =================================================================
        valid_detections = [d for d in frame_detections if d is not None and d.confidence >= 0.3]

        if not valid_detections:
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
                "overall_score": 0,
                "movements": [],
                "combination_analysis": None,
                "error": "No movements detected. Please ensure the athlete is visible."
            }

        # Count movement occurrences and track segments
        movement_counts = {}
        movement_segments = {}
        prev_movement = None

        for det in valid_detections:
            name = det.movement_name
            if name not in movement_counts:
                movement_counts[name] = {
                    'count': 0,
                    'total_confidence': 0,
                    'category': det.category.value if det.category else 'unknown',
                    'name_pt': det.movement_name_pt
                }
                movement_segments[name] = 0
            movement_counts[name]['count'] += 1
            movement_counts[name]['total_confidence'] += det.confidence

            # Count segments (distinct appearances)
            if name != prev_movement:
                movement_segments[name] += 1
            prev_movement = name

        # Sort by segment count first, then by frame count
        sorted_movements = sorted(
            movement_counts.items(),
            key=lambda x: (movement_segments[x[0]], x[1]['count']),
            reverse=True
        )

        # Filter out 'ginga' if it dominates but other movements exist
        non_ginga_movements = [(n, i) for n, i in sorted_movements if n != 'ginga']
        if non_ginga_movements and len(non_ginga_movements) >= 1:
            ginga_info = next(((n, i) for n, i in sorted_movements if n == 'ginga'), None)
            sorted_movements = non_ginga_movements
            if ginga_info:
                sorted_movements.append(ginga_info)

        # =================================================================
        # COMBINATION/SEQUENCE ANALYSIS
        # =================================================================
        combination_result = analyze_combination(frame_detections, fps=video_info.fps)

        # =================================================================
        # SCORE DETECTED MOVEMENTS
        # =================================================================
        # Map detected movements to scorers
        selected_movements = []
        detected_movement_names = []  # Keep track of original detected names
        for name, info in sorted_movements[:6]:  # Top 6 movements
            scorer_key = DETECTOR_TO_SCORER.get(name)
            if scorer_key and scorer_key not in selected_movements:
                selected_movements.append(scorer_key)
                detected_movement_names.append({
                    'detected_name': name,
                    'scorer_key': scorer_key,
                    'count': info['count'],
                    'segments': movement_segments[name],
                    'category': info['category'],
                    'name_pt': info['name_pt'],
                    'avg_confidence': info['total_confidence'] / info['count']
                })

        if not selected_movements:
            selected_movements = ['Ginga']

        # Score selected movements
        results = []
        for i, movement_name in enumerate(selected_movements):
            scorer_class = AVAILABLE_MOVEMENTS.get(movement_name)
            if not scorer_class:
                continue

            scorer = scorer_class()

            valid_angles = [a for a in all_angles if a]
            valid_timestamps = timestamps[:len(valid_angles)]

            movement_score = scorer.score_sequence(valid_angles, valid_timestamps)

            # Get the detected name info if available
            detected_info = detected_movement_names[i] if i < len(detected_movement_names) else None

            # Use the DETECTED movement name (e.g., meia_lua_de_compasso) not the scorer name
            display_name = detected_info['name_pt'] if detected_info else scorer.movement_name

            # Build result dictionary
            res = {
                "movement_name": display_name,
                "detected_as": detected_info['detected_name'] if detected_info else movement_name,
                "category": detected_info['category'] if detected_info else 'unknown',
                "detection_count": detected_info['count'] if detected_info else 0,
                "detection_segments": detected_info['segments'] if detected_info else 0,
                "detection_confidence": round(detected_info['avg_confidence'] * 100, 1) if detected_info else 0,
                "overall_score": float(movement_score.overall_score),
                "peak_score": float(movement_score.peak_score),
                "average_score": float(movement_score.average_score),
                "lowest_score": float(movement_score.lowest_score),
                "frames_analyzed": movement_score.frames_analyzed,
                "feedback": movement_score.feedback_summary if movement_score.feedback_summary else [],
                "frame_scores": [float(fs.overall_score) for fs in movement_score.frame_scores[:100]]  # Limit for response size
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
            "movements": results,
            "combination_analysis": {
                "overall_score": combination_result.overall_score,
                "level": combination_result.level.value,
                "transition_score": combination_result.transition_score,
                "rhythm_score": combination_result.rhythm_score,
                "sequence_logic_score": combination_result.sequence_logic_score,
                "recovery_score": combination_result.recovery_score,
                "variety_score": combination_result.variety_score,
                "total_movements": combination_result.total_movements,
                "unique_movements": combination_result.unique_movements,
                "transitions_analyzed": combination_result.transitions_analyzed,
                "smooth_transitions": combination_result.smooth_transitions,
                "movement_sequence": combination_result.movement_sequence[:20],  # Limit for response
                "strengths": combination_result.strengths,
                "areas_to_improve": combination_result.areas_to_improve
            },
            "detected_movements_raw": [
                {
                    "name": name,
                    "count": info['count'],
                    "segments": movement_segments[name],
                    "category": info['category'],
                    "name_pt": info['name_pt']
                }
                for name, info in sorted_movements[:10]
            ]
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
