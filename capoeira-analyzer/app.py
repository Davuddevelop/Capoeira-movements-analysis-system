"""
Capoeira Movement Analysis System - Streamlit Web Interface

This is the web interface for the Capoeira Movement Analysis System.
It provides a user-friendly way to upload videos, analyze movements,
and view reports.

Run with: streamlit run app.py

Project by: Azerbaijan Capoeira Federation
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from analyzer.pose_detector import PoseDetector, get_detection_stats
from analyzer.angle_calculator import AngleCalculator
from analyzer.report_generator import (
    ReportGenerator, SessionReport, AthleteInfo, MovementResult
)
from analyzer.movement_detector import MovementDetector, MovementCategory
from analyzer.flawlessness import analyze_flawlessness, FlawlessnessLevel
from movements import (
    GingaScorer, AuScorer, MeiaLuaScorer, ArmadaScorer, BencaoScorer,
    QueixadaScorer, MarteloScorer, EsquivaScorer, NegativaScorer,
    AVAILABLE_SCORERS
)


# Page configuration
st.set_page_config(
    page_title="Capoeira Movement Analysis",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Available movement scorers
AVAILABLE_MOVEMENTS = {
    'Ginga': GingaScorer,
    'Au (Cartwheel)': AuScorer,
    'Meia-lua de Frente': MeiaLuaScorer,
    'Armada': ArmadaScorer,
    'Bencao': BencaoScorer,
    'Queixada': QueixadaScorer,
    'Martelo': MarteloScorer,
    'Esquiva': EsquivaScorer,
    'Negativa': NegativaScorer,
}

# Mapping from detector names to scorer keys
DETECTOR_TO_SCORER = {
    'ginga': 'Ginga',
    'armada': 'Armada',
    'meia_lua_de_frente': 'Meia-lua de Frente',
    'bencao': 'Bencao',
    'queixada': 'Queixada',
    'martelo': 'Martelo',
    'au': 'Au (Cartwheel)',
    'au_batido': 'Au (Cartwheel)',
    'esquiva_lateral': 'Esquiva',
    'esquiva_baixa': 'Esquiva',
    'cocorinha': 'Esquiva',
    'negativa': 'Negativa',
    'role': 'Negativa',
    'bananeira': 'Au (Cartwheel)',
    'ponte': 'Au (Cartwheel)',
    'meia_lua_de_compasso': 'Meia-lua de Frente',
    'chapa': 'Bencao',
    'ponteira': 'Bencao',
    'gancho': 'Martelo',
}


def get_score_color(score: float) -> str:
    """Get color for score display."""
    if score >= 7:
        return "green"
    elif score >= 5:
        return "orange"
    else:
        return "red"


def display_score_card(label: str, score: float):
    """Display a score card with color coding."""
    color = get_score_color(score)
    st.markdown(f"""
    <div style="
        background-color: {color};
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
    ">
        <h4 style="margin: 0; color: white;">{label}</h4>
        <h2 style="margin: 5px 0; color: white;">{score:.1f}/10</h2>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""

    # Header
    st.title("🥋 Capoeira Movement Analysis System")
    st.markdown("**Azerbaijan Capoeira Federation**")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Athlete information
        st.subheader("Athlete Information")
        athlete_name = st.text_input("Athlete Name", value="")

        # Auto-detection mode
        st.subheader("Detection Mode")
        auto_detect = st.checkbox("Auto-detect movements", value=True,
                                  help="Automatically identify which movements are being performed")

        # Movement selection (only if not auto-detecting)
        if not auto_detect:
            st.subheader("Movements to Analyze")
            selected_movements = []
            for movement_name in AVAILABLE_MOVEMENTS.keys():
                if st.checkbox(movement_name, value=(movement_name == 'Ginga')):
                    selected_movements.append(movement_name)
        else:
            selected_movements = []
            st.info("Movements will be automatically detected from the video")

        # Options
        st.subheader("Options")
        save_annotated = st.checkbox("Save annotated video", value=False)
        show_raw_data = st.checkbox("Show raw angle data", value=False)
        show_flawlessness = st.checkbox("Show flawlessness analysis", value=True)

        # Calibration status
        st.subheader("Calibration Status")
        with st.expander("View calibration details"):
            for name, scorer_class in AVAILABLE_MOVEMENTS.items():
                scorer = scorer_class()
                status = "✓ Calibrated" if scorer.is_calibrated() else "⚠️ Placeholder"
                st.text(f"{scorer.movement_name}: {status}")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📹 Video Upload")

        uploaded_file = st.file_uploader(
            "Choose a capoeira video",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Upload a video of capoeira movements to analyze"
        )

        if uploaded_file is not None:
            # Display video preview
            st.video(uploaded_file)

    with col2:
        st.header("📊 Quick Info")

        if uploaded_file is not None:
            st.info(f"**File:** {uploaded_file.name}")
            st.info(f"**Size:** {uploaded_file.size / 1024 / 1024:.2f} MB")
            if auto_detect:
                st.success("**Mode:** Auto-detection")
            else:
                st.info(f"**Movements:** {len(selected_movements)} selected")
        else:
            st.warning("Upload a video to begin analysis")

    st.markdown("---")

    # Analyze button
    if uploaded_file is not None:
        if not auto_detect and not selected_movements:
            st.warning("Please select at least one movement to analyze or enable auto-detection")
        elif not athlete_name:
            st.warning("Please enter the athlete's name")
        else:
            if st.button("🔍 Analyze Video", type="primary", use_container_width=True):
                analyze_uploaded_video(
                    uploaded_file,
                    athlete_name,
                    selected_movements,
                    auto_detect,
                    save_annotated,
                    show_raw_data,
                    show_flawlessness
                )


def analyze_uploaded_video(uploaded_file, athlete_name: str,
                          selected_movements: list, auto_detect: bool,
                          save_annotated: bool, show_raw_data: bool,
                          show_flawlessness: bool):
    """Analyze the uploaded video file."""

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_file.read())
        video_path = tmp_file.name

    try:
        # Initialize components
        pose_detector = PoseDetector(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        angle_calculator = AngleCalculator(min_visibility=0.5)
        movement_detector = MovementDetector(min_confidence=0.4)

        # Get video info
        video_info = pose_detector.get_video_info(video_path)

        # Display video info
        st.subheader("📋 Video Information")
        info_cols = st.columns(4)
        with info_cols[0]:
            st.metric("Resolution", f"{video_info.width}x{video_info.height}")
        with info_cols[1]:
            st.metric("FPS", f"{video_info.fps:.1f}")
        with info_cols[2]:
            st.metric("Duration", f"{video_info.duration:.1f}s")
        with info_cols[3]:
            st.metric("Total Frames", video_info.total_frames)

        # Process video with progress bar
        st.subheader("⏳ Processing Video")
        progress_bar = st.progress(0)
        status_text = st.empty()

        all_angles = []
        all_landmarks = []
        frame_results = []
        timestamps = []
        frame_detections = []

        for result in pose_detector.process_video(video_path, draw_skeleton=True):
            frame_results.append(result)

            if result.pose_detected and result.landmarks:
                angles = angle_calculator.calculate_all_angles(result.landmarks.landmark)
                all_angles.append(angles)
                all_landmarks.append(result.landmarks)
                timestamps.append(result.timestamp)

                # Detect movement in this frame
                if auto_detect:
                    detection = movement_detector.detect(result.landmarks, angles)
                    frame_detections.append(detection)
            else:
                all_angles.append({})
                all_landmarks.append(None)
                if auto_detect:
                    frame_detections.append(None)

            # Update progress
            progress = (result.frame_number + 1) / video_info.total_frames
            progress_bar.progress(progress)
            status_text.text(f"Processing frame {result.frame_number + 1}/{video_info.total_frames}")

        progress_bar.progress(1.0)
        status_text.text("Processing complete!")

        # Get detection statistics
        stats = get_detection_stats(frame_results)

        st.subheader("🎯 Detection Statistics")
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("Frames with Pose", f"{stats['detected_frames']}/{stats['total_frames']}")
        with stat_cols[1]:
            st.metric("Detection Rate", f"{stats['detection_percentage']:.1f}%")
        with stat_cols[2]:
            st.metric("Missed Frames", stats['missed_frames'])

        # Auto-detect movements if enabled
        if auto_detect:
            st.subheader("🔎 Detected Movements")

            valid_detections = [d for d in frame_detections if d is not None and d.confidence >= 0.4]

            if valid_detections:
                # Count movement occurrences
                movement_counts = {}
                for det in valid_detections:
                    name = det.movement_name
                    if name not in movement_counts:
                        movement_counts[name] = {
                            'count': 0,
                            'total_confidence': 0,
                            'category': det.category,
                            'name_pt': det.movement_name_pt
                        }
                    movement_counts[name]['count'] += 1
                    movement_counts[name]['total_confidence'] += det.confidence

                # Sort by count
                sorted_movements = sorted(
                    movement_counts.items(),
                    key=lambda x: x[1]['count'],
                    reverse=True
                )

                # Display detected movements
                det_cols = st.columns(min(len(sorted_movements[:4]), 4))
                for i, (name, info) in enumerate(sorted_movements[:4]):
                    with det_cols[i]:
                        pct = (info['count'] / len(valid_detections)) * 100
                        avg_conf = info['total_confidence'] / info['count']
                        st.metric(
                            info['name_pt'],
                            f"{pct:.0f}%",
                            f"Conf: {avg_conf:.0%}"
                        )

                # Map detected movements to scorers
                selected_movements = []
                for name, info in sorted_movements[:3]:
                    scorer_key = DETECTOR_TO_SCORER.get(name)
                    if scorer_key and scorer_key not in selected_movements:
                        selected_movements.append(scorer_key)

                if not selected_movements:
                    selected_movements = ['Ginga']  # Fallback
                    st.warning("Could not map detected movements. Defaulting to Ginga.")
            else:
                st.warning("No movements detected with high confidence. Defaulting to Ginga analysis.")
                selected_movements = ['Ginga']

        # Score movements
        st.subheader("📈 Movement Scores")

        movement_results = []
        flawlessness_results = {}

        for movement_name in selected_movements:
            scorer_class = AVAILABLE_MOVEMENTS.get(movement_name)
            if not scorer_class:
                continue

            scorer = scorer_class()

            # Filter to valid angles
            valid_angles = [a for a in all_angles if a]
            valid_timestamps = timestamps[:len(valid_angles)]

            movement_score = scorer.score_sequence(valid_angles, valid_timestamps)

            # Perform flawlessness analysis
            frame_scores_list = [fs.overall_score for fs in movement_score.frame_scores]
            frame_angles_list = [fs.angles for fs in movement_score.frame_scores]
            flawlessness = analyze_flawlessness(
                frame_scores_list,
                frame_angles_list,
                scorer.movement_name
            )
            flawlessness_results[movement_name] = flawlessness

            # Create MovementResult
            feedback = movement_score.feedback_summary.copy() if movement_score.feedback_summary else []
            if show_flawlessness:
                feedback.extend(flawlessness.feedback)

            result = MovementResult(
                movement_name=scorer.movement_name,
                overall_score=movement_score.overall_score,
                peak_score=movement_score.peak_score,
                lowest_score=movement_score.lowest_score,
                average_score=movement_score.average_score,
                frames_analyzed=movement_score.frames_analyzed,
                frames_with_pose=movement_score.frames_with_pose,
                feedback=feedback,
                frame_scores=[fs.overall_score for fs in movement_score.frame_scores]
            )

            # Collect angle data
            angle_data = {}
            for key in ['left_knee', 'right_knee', 'left_hip', 'right_hip', 'spine']:
                angle_data[key] = []
                for fs in movement_score.frame_scores:
                    if fs.angles and key in fs.angles and fs.angles[key] is not None:
                        angle_data[key].append(fs.angles[key])
            result.angle_data = angle_data

            movement_results.append(result)

        # Display movement scores
        score_cols = st.columns(len(movement_results))
        for i, result in enumerate(movement_results):
            with score_cols[i]:
                display_score_card(result.movement_name, result.overall_score)

        # Detailed results expander
        for result in movement_results:
            with st.expander(f"📋 {result.movement_name} Details"):
                detail_cols = st.columns(4)
                with detail_cols[0]:
                    st.metric("Average Score", f"{result.average_score:.1f}")
                with detail_cols[1]:
                    st.metric("Peak Score", f"{result.peak_score:.1f}")
                with detail_cols[2]:
                    st.metric("Lowest Score", f"{result.lowest_score:.1f}")
                with detail_cols[3]:
                    st.metric("Frames Analyzed", result.frames_with_pose)

                if result.feedback:
                    st.markdown("**Feedback:**")
                    for fb in result.feedback:
                        st.markdown(f"- {fb}")

                # Score chart
                if result.frame_scores:
                    st.markdown("**Score Over Time:**")
                    st.line_chart(result.frame_scores)

                # Angle data
                if show_raw_data and result.angle_data:
                    st.markdown("**Angle Data:**")
                    import pandas as pd
                    df = pd.DataFrame(result.angle_data)
                    st.dataframe(df)

        # Overall score
        if movement_results:
            overall_score = sum(m.overall_score for m in movement_results) / len(movement_results)

            st.markdown("---")
            st.subheader("🏆 Overall Session Score")

            center_col = st.columns([1, 2, 1])[1]
            with center_col:
                display_score_card("Overall Score", overall_score)

        # Generate report
        st.markdown("---")
        st.subheader("📄 Download Report")

        athlete = AthleteInfo(name=athlete_name)
        session = SessionReport(
            athlete=athlete,
            video_path=uploaded_file.name,
            video_duration=video_info.duration,
            total_frames=video_info.total_frames,
            movements=movement_results,
            overall_score=overall_score if movement_results else 0,
            detection_rate=stats['detection_percentage']
        )

        report_generator = ReportGenerator()

        # Text report
        text_report = report_generator.generate_text_report(session)
        st.download_button(
            label="📝 Download Text Report",
            data=text_report,
            file_name=f"report_{session.athlete.session_id}.txt",
            mime="text/plain"
        )

        # HTML report
        html_report = report_generator.generate_html_report(session)
        st.download_button(
            label="🌐 Download HTML Report",
            data=html_report,
            file_name=f"report_{session.athlete.session_id}.html",
            mime="text/html"
        )

        st.success("✅ Analysis complete!")

    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        raise e

    finally:
        # Clean up temporary file
        try:
            os.unlink(video_path)
        except:
            pass


# Footer
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Capoeira Movement Analysis System v1.0</p>
        <p>Project by Azerbaijan Capoeira Federation</p>
        <p>⚠️ All scoring criteria are placeholders to be calibrated with the coach</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
    show_footer()
