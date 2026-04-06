"""
Capoeira Movement Analysis System - Streamlit Web Interface

Automatic movement detection and analysis - no manual selection needed.
The system detects movements, scores them, and analyzes the overall sequence flow.

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
from analyzer.combination_analyzer import analyze_combination, CombinationLevel
from movements import (
    GingaScorer, AuScorer, MeiaLuaScorer, ArmadaScorer, BencaoScorer,
    QueixadaScorer, MarteloScorer, EsquivaScorer, NegativaScorer,
    AVAILABLE_SCORERS
)


# Page configuration
st.set_page_config(
    page_title="Capoeira Movement Analysis",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    'ginga_baixa': 'Ginga',
    'armada': 'Armada',
    'meia_lua_de_frente': 'Meia-lua de Frente',
    'bencao': 'Bencao',
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
    'chapa': 'Bencao',
    'ponteira': 'Bencao',
    'pisao': 'Bencao',
    'gancho': 'Martelo',
    'chibata': 'Martelo',
    'joelhada': 'Bencao',
    'cotovelhada': 'Bencao',
    'cabecada': 'Bencao',
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
    st.title("🥋 Capoeira Movement Analysis")
    st.caption("Azerbaijan Capoeira Federation - Fully Automatic Movement Detection")

    # Just video upload - nothing else needed
    uploaded_file = st.file_uploader(
        "📹 Upload capoeira video (movements detected automatically)",
        type=['mp4', 'avi', 'mov', 'mkv'],
    )

    if uploaded_file is not None:
        st.video(uploaded_file)

        # Optional name field with default
        athlete_name = st.text_input("Athlete name (optional)", value="Athlete")

        # ONE BUTTON - fully automatic
        if st.button("🔍 ANALYZE VIDEO", type="primary", use_container_width=True):
            analyze_video(uploaded_file, athlete_name)


def analyze_video(uploaded_file, athlete_name: str):
    """Analyze the uploaded video with automatic movement detection."""

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
        frame_results = []
        timestamps = []
        frame_detections = []

        for result in pose_detector.process_video(video_path, draw_skeleton=True):
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

            # Update progress
            progress = (result.frame_number + 1) / video_info.total_frames
            progress_bar.progress(progress)
            status_text.text(f"Processing frame {result.frame_number + 1}/{video_info.total_frames}")

        progress_bar.progress(1.0)
        status_text.text("Processing complete!")

        # Get detection statistics
        stats = get_detection_stats(frame_results)

        st.subheader("🎯 Pose Detection Results")
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("Frames with Pose", f"{stats['detected_frames']}/{stats['total_frames']}")
        with stat_cols[1]:
            st.metric("Detection Rate", f"{stats['detection_percentage']:.1f}%")
        with stat_cols[2]:
            st.metric("Missed Frames", stats['missed_frames'])

        # =====================================================================
        # AUTO-DETECTED MOVEMENTS
        # =====================================================================
        st.subheader("🔎 Detected Movements")

        # Lower confidence threshold to catch more movements
        valid_detections = [d for d in frame_detections if d is not None and d.confidence >= 0.3]

        if not valid_detections:
            st.warning("No movements detected. Please ensure the athlete is visible in the video.")
            return

        # Count movement occurrences - but also track distinct movement segments
        movement_counts = {}
        movement_segments = {}  # Track how many separate times each movement appears

        prev_movement = None
        for det in valid_detections:
            name = det.movement_name
            if name not in movement_counts:
                movement_counts[name] = {
                    'count': 0,
                    'total_confidence': 0,
                    'category': det.category,
                    'name_pt': det.movement_name_pt
                }
                movement_segments[name] = 0
            movement_counts[name]['count'] += 1
            movement_counts[name]['total_confidence'] += det.confidence

            # Count segments (distinct appearances)
            if name != prev_movement:
                movement_segments[name] += 1
            prev_movement = name

        # Sort by SEGMENT COUNT first, then by frame count
        # This prioritizes movements that appear distinctly multiple times
        sorted_movements = sorted(
            movement_counts.items(),
            key=lambda x: (movement_segments[x[0]], x[1]['count']),
            reverse=True
        )

        # Filter out 'ginga' if it dominates but other movements exist
        # Ginga is the base movement, other movements are more interesting
        non_ginga_movements = [(n, i) for n, i in sorted_movements if n != 'ginga']
        if non_ginga_movements and len(non_ginga_movements) >= 2:
            # Show non-ginga movements first, then ginga
            ginga_info = next(((n, i) for n, i in sorted_movements if n == 'ginga'), None)
            sorted_movements = non_ginga_movements
            if ginga_info:
                sorted_movements.append(ginga_info)

        # Display detected movements - show up to 6
        num_to_show = min(len(sorted_movements), 6)
        det_cols = st.columns(min(num_to_show, 4))
        for i, (name, info) in enumerate(sorted_movements[:4]):
            with det_cols[i % 4]:
                pct = (info['count'] / len(valid_detections)) * 100
                avg_conf = info['total_confidence'] / info['count']
                segments = movement_segments[name]
                st.metric(
                    info['name_pt'],
                    f"{segments}x" if segments > 1 else f"{pct:.0f}%",
                    f"Conf: {avg_conf:.0%}"
                )

        # Map detected movements to scorers - use more movements
        selected_movements = []
        for name, info in sorted_movements[:5]:  # Increased from 3 to 5
            scorer_key = DETECTOR_TO_SCORER.get(name)
            if scorer_key and scorer_key not in selected_movements:
                selected_movements.append(scorer_key)

        if not selected_movements:
            selected_movements = ['Ginga']

        # =====================================================================
        # MOVEMENT SEQUENCE / COMBINATION ANALYSIS
        # =====================================================================
        st.subheader("🌊 Movement Sequence Analysis")

        combination_result = analyze_combination(frame_detections, fps=video_info.fps)

        # Flow level color mapping
        flow_colors = {
            'Master Flow': '#FFD700',
            'Expert Flow': '#00FF00',
            'Advanced Flow': '#90EE90',
            'Intermediate': '#87CEEB',
            'Developing': '#FFA500',
            'Beginner': '#FF6347',
            'Novice': '#FF0000'
        }
        flow_color = flow_colors.get(combination_result.level.value, '#808080')

        # Main flow score display
        flow_cols = st.columns([1, 2, 1])
        with flow_cols[1]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {flow_color}, {flow_color}88);
                color: black;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                margin: 10px 0;
            ">
                <h3 style="margin: 0; color: black;">Sequence Quality</h3>
                <h1 style="margin: 10px 0; color: black; font-size: 2.5em;">{combination_result.level.value}</h1>
                <h2 style="margin: 0; color: black;">{combination_result.overall_score:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)

        # Component scores
        comp_cols = st.columns(5)
        components = [
            ("Transitions", combination_result.transition_score),
            ("Rhythm", combination_result.rhythm_score),
            ("Sequence Logic", combination_result.sequence_logic_score),
            ("Recovery", combination_result.recovery_score),
            ("Variety", combination_result.variety_score),
        ]
        for i, (name, score) in enumerate(components):
            with comp_cols[i]:
                st.metric(name, f"{score:.0f}%")

        # Movement sequence visualization
        if combination_result.movement_sequence:
            st.markdown("**Movement Flow:**")
            seq_display = " → ".join(combination_result.movement_sequence[:15])
            if len(combination_result.movement_sequence) > 15:
                seq_display += f" ... (+{len(combination_result.movement_sequence) - 15} more)"
            st.code(seq_display)

            seq_cols = st.columns(3)
            with seq_cols[0]:
                st.metric("Total Movements", combination_result.total_movements)
            with seq_cols[1]:
                st.metric("Unique Movements", combination_result.unique_movements)
            with seq_cols[2]:
                st.metric("Smooth Transitions", f"{combination_result.smooth_transitions}/{combination_result.transitions_analyzed}")

        # Feedback
        feedback_cols = st.columns(2)
        with feedback_cols[0]:
            if combination_result.strengths:
                st.markdown("**✓ Strengths:**")
                for s in combination_result.strengths:
                    st.success(s)
        with feedback_cols[1]:
            if combination_result.areas_to_improve:
                st.markdown("**→ Areas to Improve:**")
                for a in combination_result.areas_to_improve:
                    st.warning(a)

        # =====================================================================
        # INDIVIDUAL MOVEMENT SCORES
        # =====================================================================
        st.subheader("📈 Individual Movement Scores")

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
        if movement_results:
            score_cols = st.columns(len(movement_results))
            for i, result in enumerate(movement_results):
                with score_cols[i]:
                    display_score_card(result.movement_name, result.overall_score)

        # Display flawlessness ratings
        if flawlessness_results:
            st.subheader("💎 Flawlessness Analysis")
            flaw_cols = st.columns(len(flawlessness_results))
            for i, (name, flawlessness) in enumerate(flawlessness_results.items()):
                with flaw_cols[i]:
                    level_color = {
                        'Flawless': '#FFD700',
                        'Excellent': '#00FF00',
                        'Very Good': '#90EE90',
                        'Good': '#87CEEB',
                        'Fair': '#FFA500',
                        'Needs Work': '#FF6347',
                        'Poor': '#FF0000'
                    }.get(flawlessness.level.value, '#808080')

                    st.markdown(f"""
                    <div style="
                        background-color: {level_color};
                        color: black;
                        padding: 10px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 5px;
                    ">
                        <h4 style="margin: 0; color: black;">{name}</h4>
                        <h3 style="margin: 5px 0; color: black;">{flawlessness.level.value}</h3>
                        <p style="margin: 0; color: black;">{flawlessness.overall_score:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)

        # Detailed results
        for result in movement_results:
            with st.expander(f"📋 {result.movement_name} - Detailed Analysis"):
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

                if result.frame_scores:
                    st.markdown("**Score Over Time:**")
                    st.line_chart(result.frame_scores)

        # =====================================================================
        # OVERALL SCORE
        # =====================================================================
        if movement_results:
            overall_score = sum(m.overall_score for m in movement_results) / len(movement_results)

            st.markdown("---")
            st.subheader("🏆 Overall Performance")

            center_col = st.columns([1, 2, 1])[1]
            with center_col:
                display_score_card("Overall Score", overall_score)

        # =====================================================================
        # DOWNLOAD REPORTS
        # =====================================================================
        st.markdown("---")
        st.subheader("📄 Download Reports")

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

        report_cols = st.columns(2)
        with report_cols[0]:
            text_report = report_generator.generate_text_report(session)
            st.download_button(
                label="📝 Download Text Report",
                data=text_report,
                file_name=f"capoeira_report_{athlete_name.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with report_cols[1]:
            html_report = report_generator.generate_html_report(session)
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_report,
                file_name=f"capoeira_report_{athlete_name.replace(' ', '_')}.html",
                mime="text/html",
                use_container_width=True
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
        <p>Capoeira Movement Analysis System v2.0</p>
        <p>Azerbaijan Capoeira Federation</p>
        <p>✓ Automatic movement detection - no manual selection needed</p>
        <p>✓ Sequence/combination flow analysis</p>
        <p>✓ Biomechanically calibrated scoring</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
    show_footer()
