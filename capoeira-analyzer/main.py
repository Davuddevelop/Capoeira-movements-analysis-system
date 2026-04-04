"""
Capoeira Movement Analysis System - Main Entry Point

This is the command-line interface for the Capoeira Movement Analysis System.
It allows you to analyze capoeira videos, detect poses, calculate joint angles,
and score movements based on predefined criteria.

Usage:
    python main.py analyze <video_path> [options]
    python main.py info <video_path>
    python main.py test

Project by: Azerbaijan Capoeira Federation
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from analyzer.pose_detector import PoseDetector, get_detection_stats
from analyzer.angle_calculator import AngleCalculator
from analyzer.movement_scorer import MovementScorer, MovementScore
from analyzer.report_generator import (
    ReportGenerator, SessionReport, AthleteInfo, MovementResult
)
from analyzer.movement_detector import MovementDetector, MovementCategory
from movements import (
    GingaScorer, AuScorer, MeiaLuaScorer, ArmadaScorer, BencaoScorer,
    QueixadaScorer, MarteloScorer, EsquivaScorer, NegativaScorer,
    AVAILABLE_SCORERS
)
from analyzer.flawlessness import analyze_flawlessness, FlawlessnessLevel


# Available movement scorers
AVAILABLE_MOVEMENTS = {
    'ginga': GingaScorer,
    'au': AuScorer,
    'meia_lua': MeiaLuaScorer,
    'armada': ArmadaScorer,
    'bencao': BencaoScorer,
    'queixada': QueixadaScorer,
    'martelo': MarteloScorer,
    'esquiva': EsquivaScorer,
    'negativa': NegativaScorer,
}


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("  CAPOEIRA MOVEMENT ANALYSIS SYSTEM")
    print("  Azerbaijan Capoeira Federation")
    print("=" * 60)
    print()


def print_progress(current: int, total: int):
    """Print a simple progress indicator."""
    percentage = (current / total) * 100 if total > 0 else 0
    bar_length = 40
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\rProcessing: [{bar}] {percentage:.1f}% ({current}/{total} frames)", end='', flush=True)


def analyze_video(video_path: str,
                 athlete_name: str = "Unknown Athlete",
                 movements: List[str] = None,
                 auto_detect: bool = True,
                 output_format: str = "text",
                 save_annotated: bool = False,
                 verbose: bool = True) -> SessionReport:
    """
    Analyze a capoeira video for movement quality.

    Args:
        video_path: Path to the video file
        athlete_name: Name of the athlete
        movements: List of movements to analyze (if auto_detect=False)
        auto_detect: Whether to automatically detect movements
        output_format: 'text' or 'html'
        save_annotated: Whether to save annotated video
        verbose: Whether to print progress

    Returns:
        SessionReport with analysis results
    """
    # Validate video path
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if verbose:
        print(f"Analyzing video: {video_path.name}")
        print(f"Athlete: {athlete_name}")
        print(f"Mode: {'Automatic Detection' if auto_detect else 'Manual Selection'}")
        print()

    # Initialize components
    pose_detector = PoseDetector(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    )
    angle_calculator = AngleCalculator(min_visibility=0.5)
    movement_detector = MovementDetector(min_confidence=0.4)

    # Get video info
    video_info = pose_detector.get_video_info(str(video_path))
    if verbose:
        print(f"Video Info:")
        print(f"  Resolution: {video_info.width}x{video_info.height}")
        print(f"  FPS: {video_info.fps:.2f}")
        print(f"  Duration: {video_info.duration:.2f}s")
        print(f"  Total Frames: {video_info.total_frames}")
        print()

    # Process video frames
    all_angles = []
    all_landmarks = []
    frame_results = []
    timestamps = []
    frame_detections = []

    if verbose:
        print("Processing video frames...")

    callback = print_progress if verbose else None

    for result in pose_detector.process_video(str(video_path),
                                              draw_skeleton=True,
                                              progress_callback=callback):
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

    if verbose:
        print("\n")

    # Get detection statistics
    stats = get_detection_stats(frame_results)
    if verbose:
        print(f"Detection Statistics:")
        print(f"  Frames with pose: {stats['detected_frames']}/{stats['total_frames']}")
        print(f"  Detection rate: {stats['detection_percentage']:.1f}%")
        print()

    # Determine which movements to score
    scorers = []
    detected_movements = {}

    if auto_detect:
        # Analyze frame detections to find dominant movements
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

            # Sort by count and filter significant movements
            sorted_movements = sorted(
                movement_counts.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )

            if verbose:
                print("Detected Movements:")
                for name, info in sorted_movements[:5]:  # Show top 5
                    pct = (info['count'] / len(valid_detections)) * 100
                    avg_conf = info['total_confidence'] / info['count']
                    print(f"  {info['name_pt']}: {pct:.1f}% of frames (avg confidence: {avg_conf:.2f})")
                print()

            # Get scorers for detected movements (top 3)
            for name, info in sorted_movements[:3]:
                # Map detector names to scorer names
                scorer_name = _map_detector_to_scorer(name)
                if scorer_name and scorer_name in AVAILABLE_SCORERS:
                    scorer = AVAILABLE_SCORERS[scorer_name]()
                    scorers.append(scorer)
                    detected_movements[scorer_name] = info
                    if verbose:
                        calibrated = "Yes" if scorer.is_calibrated() else "No (placeholder values)"
                        print(f"Scoring: {scorer.movement_name} - Calibrated: {calibrated}")

        if not scorers and verbose:
            print("No specific movements detected with high confidence.")
            print("Defaulting to Ginga analysis...")

    if not auto_detect or not scorers:
        # Manual mode or fallback
        if movements is None:
            movements = ['ginga']  # Default
        else:
            movements = [m.lower() for m in movements]

        for movement in movements:
            if movement in AVAILABLE_SCORERS:
                scorer = AVAILABLE_SCORERS[movement]()
                scorers.append(scorer)
                if verbose:
                    calibrated = "Yes" if scorer.is_calibrated() else "No (placeholder values)"
                    print(f"Movement: {scorer.movement_name} - Calibrated: {calibrated}")
            else:
                print(f"Warning: Unknown movement '{movement}', skipping...")

    if not scorers:
        raise ValueError("No valid movements to analyze")

    print()

    # Score each movement
    movement_results = []

    for scorer in scorers:
        if verbose:
            print(f"Scoring {scorer.movement_name}...")

        # Filter to only frames with valid angles
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

        # Create MovementResult for the report
        result = MovementResult(
            movement_name=scorer.movement_name,
            overall_score=movement_score.overall_score,
            peak_score=movement_score.peak_score,
            lowest_score=movement_score.lowest_score,
            average_score=movement_score.average_score,
            frames_analyzed=movement_score.frames_analyzed,
            frames_with_pose=movement_score.frames_with_pose,
            feedback=movement_score.feedback_summary + flawlessness.feedback,
            frame_scores=frame_scores_list
        )

        # Collect angle data for graphs
        angle_data = {}
        for key in ['left_knee', 'right_knee', 'left_hip', 'right_hip',
                    'left_elbow', 'right_elbow', 'spine']:
            angle_data[key] = []
            for fs in movement_score.frame_scores:
                if fs.angles and key in fs.angles and fs.angles[key] is not None:
                    angle_data[key].append(fs.angles[key])

        result.angle_data = angle_data
        movement_results.append(result)

        if verbose:
            print(f"  Score: {result.overall_score:.1f}/10")
            print(f"  Flawlessness: {flawlessness.level.value} ({flawlessness.overall_score:.1f}%)")
            print(f"  Peak: {result.peak_score:.1f}, Lowest: {result.lowest_score:.1f}")
            print()

    # Calculate overall session score
    if movement_results:
        overall_score = sum(m.overall_score for m in movement_results) / len(movement_results)
    else:
        overall_score = 0.0

    # Create session report
    athlete = AthleteInfo(name=athlete_name)
    session = SessionReport(
        athlete=athlete,
        video_path=str(video_path),
        video_duration=video_info.duration,
        total_frames=video_info.total_frames,
        movements=movement_results,
        overall_score=overall_score,
        detection_rate=stats['detection_percentage']
    )

    # Generate and save report
    report_generator = ReportGenerator()

    if output_format == 'html':
        report_path = report_generator.save_html_report(session)
    else:
        report_path = report_generator.save_text_report(session)

    if verbose:
        print(f"Report saved to: {report_path}")

    # Save annotated video if requested
    if save_annotated:
        output_video = Path("output") / f"annotated_{video_path.name}"
        output_video.parent.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"Saving annotated video to: {output_video}")

        pose_detector.save_annotated_video(
            str(video_path),
            str(output_video),
            progress_callback=callback if verbose else None
        )

        if verbose:
            print("\nAnnotated video saved!")

    return session


def _map_detector_to_scorer(detector_name: str) -> Optional[str]:
    """Map movement detector names to scorer names."""
    mapping = {
        'ginga': 'ginga',
        'armada': 'armada',
        'meia_lua_de_frente': 'meia_lua',
        'bencao': 'bencao',
        'queixada': 'queixada',
        'martelo': 'martelo',
        'au': 'au',
        'au_batido': 'au',
        'esquiva_lateral': 'esquiva',
        'esquiva_baixa': 'esquiva',
        'cocorinha': 'esquiva',
        'negativa': 'negativa',
        'role': 'negativa',
        'bananeira': 'au',
        'ponte': 'au',
        'meia_lua_de_compasso': 'meia_lua',
        'chapa': 'bencao',
        'ponteira': 'bencao',
        'gancho': 'martelo',
    }
    return mapping.get(detector_name)


def show_video_info(video_path: str):
    """Display information about a video file."""
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        return

    pose_detector = PoseDetector()
    video_info = pose_detector.get_video_info(str(video_path))

    print(f"Video: {video_path.name}")
    print(f"  Resolution: {video_info.width}x{video_info.height}")
    print(f"  FPS: {video_info.fps:.2f}")
    print(f"  Duration: {video_info.duration:.2f} seconds")
    print(f"  Total Frames: {video_info.total_frames}")


def run_tests():
    """Run basic tests to verify the system is working."""
    print("Running system tests...")
    print()

    # Test 1: Import check
    print("Test 1: Import check...")
    try:
        from analyzer.pose_detector import PoseDetector
        from analyzer.angle_calculator import AngleCalculator
        from analyzer.movement_scorer import MovementScorer
        from analyzer.report_generator import ReportGenerator
        from movements import GingaScorer
        print("  ✓ All imports successful")
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

    # Test 2: Angle calculation
    print("Test 2: Angle calculation...")
    try:
        calc = AngleCalculator()
        # Test with a simple right angle
        angle = calc.calculate_angle((0, 0), (1, 0), (1, 1))
        assert 85 < angle < 95, f"Expected ~90°, got {angle}°"
        print(f"  ✓ Angle calculation works (got {angle:.1f}° for right angle)")
    except Exception as e:
        print(f"  ✗ Angle calculation failed: {e}")
        return False

    # Test 3: Movement scorer
    print("Test 3: Movement scorer...")
    try:
        ginga = GingaScorer()
        assert ginga.movement_name == "Ginga"
        assert len(ginga.criteria) > 0
        print(f"  ✓ Ginga scorer initialized with {len(ginga.criteria)} criteria")
    except Exception as e:
        print(f"  ✗ Movement scorer failed: {e}")
        return False

    # Test 4: Report generation
    print("Test 4: Report generation...")
    try:
        from analyzer.report_generator import create_sample_report
        sample = create_sample_report()
        generator = ReportGenerator()
        text_report = generator.generate_text_report(sample)
        assert len(text_report) > 100
        print("  ✓ Report generation works")
    except Exception as e:
        print(f"  ✗ Report generation failed: {e}")
        return False

    print()
    print("All tests passed! ✓")
    return True


def list_movements():
    """List all available movements and their calibration status."""
    print("Available Movements:")
    print("-" * 50)

    for name, scorer_class in AVAILABLE_MOVEMENTS.items():
        scorer = scorer_class()
        calibrated = "Yes" if scorer.is_calibrated() else "No (placeholder values)"
        print(f"  {scorer.movement_name}")
        print(f"    Key: {name}")
        print(f"    Calibrated: {calibrated}")
        print(f"    Criteria: {len(scorer.criteria)}")
        print()


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Capoeira Movement Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py analyze video.mp4 -n "John Doe"              # Auto-detect movements
  python main.py analyze video.mp4 -n "Jane" --no-auto        # Disable auto-detect
  python main.py analyze video.mp4 -n "Jane" -m ginga au      # Specify movements
  python main.py analyze video.mp4 -n "Jane" -f html          # HTML report
  python main.py info video.mp4
  python main.py test
  python main.py movements
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a capoeira video')
    analyze_parser.add_argument('video', help='Path to the video file')
    analyze_parser.add_argument('-n', '--name', default='Unknown Athlete',
                               help='Athlete name')
    analyze_parser.add_argument('-m', '--movements', nargs='+', default=None,
                               help='Movements to analyze (overrides auto-detection)')
    analyze_parser.add_argument('--no-auto', action='store_true',
                               help='Disable automatic movement detection')
    analyze_parser.add_argument('-f', '--format', choices=['text', 'html'], default='text',
                               help='Output format (default: text)')
    analyze_parser.add_argument('--save-video', action='store_true',
                               help='Save annotated video')
    analyze_parser.add_argument('-q', '--quiet', action='store_true',
                               help='Quiet mode (less output)')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show video information')
    info_parser.add_argument('video', help='Path to the video file')

    # Test command
    subparsers.add_parser('test', help='Run system tests')

    # Movements command
    subparsers.add_parser('movements', help='List available movements')

    # Parse arguments
    args = parser.parse_args()

    # Print header unless quiet mode
    if not (hasattr(args, 'quiet') and args.quiet):
        print_header()

    # Execute command
    if args.command == 'analyze':
        try:
            # Determine auto-detect mode
            auto_detect = not args.no_auto and args.movements is None
            analyze_video(
                video_path=args.video,
                athlete_name=args.name,
                movements=args.movements,
                auto_detect=auto_detect,
                output_format=args.format,
                save_annotated=args.save_video,
                verbose=not args.quiet
            )
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == 'info':
        show_video_info(args.video)

    elif args.command == 'test':
        success = run_tests()
        sys.exit(0 if success else 1)

    elif args.command == 'movements':
        list_movements()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
