"""
System Integration Test

This script tests the complete Capoeira Movement Analysis System by:
1. Creating a simple 5-second black video using OpenCV
2. Running it through PoseDetector
3. Confirming the system processes frames without crashing
4. Printing "SYSTEM OK" if everything works
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np


def create_test_video(output_path: str, duration_seconds: int = 5, fps: int = 30):
    """
    Create a simple black video for testing.

    Args:
        output_path: Path to save the video
        duration_seconds: Duration of video in seconds
        fps: Frames per second
    """
    width, height = 640, 480
    total_frames = duration_seconds * fps

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        raise RuntimeError(f"Could not create video file: {output_path}")

    print(f"Creating {duration_seconds}s test video ({total_frames} frames)...")

    for i in range(total_frames):
        # Create a black frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Add a white rectangle that moves (to have some variation)
        x = int((i / total_frames) * (width - 100))
        cv2.rectangle(frame, (x, 200), (x + 100, 280), (255, 255, 255), -1)

        # Add frame number text
        cv2.putText(frame, f"Frame {i}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print(f"Test video created: {output_path}")


def test_pose_detector(video_path: str):
    """
    Test the PoseDetector with the test video.

    Args:
        video_path: Path to the test video
    """
    from analyzer.pose_detector import PoseDetector, get_detection_stats

    print("\nTesting PoseDetector...")

    detector = PoseDetector(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    )

    # Get video info
    video_info = detector.get_video_info(video_path)
    print(f"  Video: {video_info.width}x{video_info.height} @ {video_info.fps}fps")
    print(f"  Total frames: {video_info.total_frames}")
    print(f"  Duration: {video_info.duration:.2f}s")

    # Process video
    results = []
    frame_count = 0

    print("  Processing frames...")
    for result in detector.process_video(video_path, draw_skeleton=True):
        results.append(result)
        frame_count += 1

        if frame_count % 30 == 0:
            print(f"    Processed {frame_count} frames...")

    # Get stats
    stats = get_detection_stats(results)
    print(f"\n  Results:")
    print(f"    Frames processed: {stats['total_frames']}")
    print(f"    Poses detected: {stats['detected_frames']}")
    print(f"    Detection rate: {stats['detection_percentage']:.1f}%")

    # Since it's a black video with no person, detection rate should be 0%
    # But the system should process all frames without crashing
    assert stats['total_frames'] > 0, "No frames processed"
    print("  PoseDetector: OK")

    return True


def test_angle_calculator():
    """Test the AngleCalculator module."""
    from analyzer.angle_calculator import AngleCalculator

    print("\nTesting AngleCalculator...")

    calc = AngleCalculator()

    # Test basic angle calculation
    angle = calc.calculate_angle((0, 0), (1, 0), (1, 1))
    assert 85 < angle < 95, f"Expected ~90°, got {angle}°"
    print(f"  90° angle test: {angle:.1f}° (OK)")

    # Test 180° angle
    angle = calc.calculate_angle((0, 0), (1, 0), (2, 0))
    assert 175 < angle < 185, f"Expected ~180°, got {angle}°"
    print(f"  180° angle test: {angle:.1f}° (OK)")

    print("  AngleCalculator: OK")
    return True


def test_movement_scorers():
    """Test all movement scorers."""
    from movements import (
        GingaScorer, AuScorer, MeiaLuaScorer, ArmadaScorer, BencaoScorer
    )

    print("\nTesting Movement Scorers...")

    scorers = [
        GingaScorer(),
        AuScorer(),
        MeiaLuaScorer(),
        ArmadaScorer(),
        BencaoScorer()
    ]

    for scorer in scorers:
        assert scorer.movement_name, f"{scorer.__class__.__name__} has no name"
        assert len(scorer.criteria) > 0, f"{scorer.movement_name} has no criteria"
        print(f"  {scorer.movement_name}: {len(scorer.criteria)} criteria")

    print("  Movement Scorers: OK")
    return True


def test_report_generator():
    """Test the report generator."""
    from analyzer.report_generator import (
        ReportGenerator, create_sample_report
    )

    print("\nTesting ReportGenerator...")

    report = create_sample_report()
    generator = ReportGenerator()

    # Generate text report
    text = generator.generate_text_report(report)
    assert len(text) > 100, "Text report too short"
    assert "CAPOEIRA" in text, "Missing header in text report"
    print(f"  Text report: {len(text)} characters (OK)")

    # Generate HTML report
    html = generator.generate_html_report(report)
    assert "<html" in html, "Missing HTML tag"
    assert "</html>" in html, "HTML not closed properly"
    print(f"  HTML report: {len(html)} characters (OK)")

    print("  ReportGenerator: OK")
    return True


def main():
    """Run all system tests."""
    print("=" * 60)
    print("CAPOEIRA MOVEMENT ANALYSIS SYSTEM - INTEGRATION TEST")
    print("=" * 60)

    all_passed = True

    # Create temporary video file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        video_path = tmp.name

    try:
        # Step 1: Create test video
        create_test_video(video_path, duration_seconds=2, fps=30)

        # Step 2: Test PoseDetector
        if not test_pose_detector(video_path):
            all_passed = False

        # Step 3: Test AngleCalculator
        if not test_angle_calculator():
            all_passed = False

        # Step 4: Test Movement Scorers
        if not test_movement_scorers():
            all_passed = False

        # Step 5: Test Report Generator
        if not test_report_generator():
            all_passed = False

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    finally:
        # Cleanup
        try:
            os.unlink(video_path)
            print(f"\nCleaned up test video: {video_path}")
        except:
            pass

    print("\n" + "=" * 60)
    if all_passed:
        print("SYSTEM OK")
        print("All components tested successfully!")
    else:
        print("SYSTEM FAILED")
        print("Some tests did not pass.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
