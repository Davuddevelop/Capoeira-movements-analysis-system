"""
Flawlessness Rating System

This module provides an advanced scoring system that goes beyond simple
angle matching to assess overall movement quality and "flawlessness".

FLAWLESSNESS CRITERIA:
1. Technical Accuracy - How close to ideal angles (40%)
2. Consistency - Maintaining form throughout (20%)
3. Fluidity - Smooth transitions, no jerky movements (15%)
4. Timing - Appropriate speed and rhythm (15%)
5. Completeness - Full execution of movement phases (10%)

RATING SCALE:
- 95-100: Flawless (Perfeito)
- 85-94: Excellent (Excelente)
- 75-84: Very Good (Muito Bom)
- 65-74: Good (Bom)
- 50-64: Fair (Regular)
- 35-49: Needs Work (Precisa Melhorar)
- 0-34: Poor (Fraco)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
from enum import Enum


class FlawlessnessLevel(Enum):
    """Flawlessness rating levels."""
    FLAWLESS = "Flawless"           # 95-100
    EXCELLENT = "Excellent"          # 85-94
    VERY_GOOD = "Very Good"          # 75-84
    GOOD = "Good"                    # 65-74
    FAIR = "Fair"                    # 50-64
    NEEDS_WORK = "Needs Work"        # 35-49
    POOR = "Poor"                    # 0-34


@dataclass
class FlawlessnessBreakdown:
    """Detailed breakdown of flawlessness score."""
    technical_accuracy: float = 0.0   # 0-100
    consistency: float = 0.0          # 0-100
    fluidity: float = 0.0             # 0-100
    timing: float = 0.0               # 0-100
    completeness: float = 0.0         # 0-100
    overall_score: float = 0.0        # 0-100
    level: FlawlessnessLevel = FlawlessnessLevel.POOR
    feedback: List[str] = field(default_factory=list)


@dataclass
class MovementPhase:
    """Represents a phase of a movement (e.g., chamber, extension, recovery)."""
    name: str
    start_frame: int
    end_frame: int
    detected: bool = False
    quality_score: float = 0.0


class FlawlessnessAnalyzer:
    """
    Analyzes movement execution for flawlessness.

    Goes beyond simple angle matching to assess:
    - Technical accuracy (correct angles)
    - Consistency (maintaining form)
    - Fluidity (smooth motion)
    - Timing (appropriate speed)
    - Completeness (all phases executed)
    """

    # Weight distribution for overall score
    WEIGHT_TECHNICAL = 0.40
    WEIGHT_CONSISTENCY = 0.20
    WEIGHT_FLUIDITY = 0.15
    WEIGHT_TIMING = 0.15
    WEIGHT_COMPLETENESS = 0.10

    def __init__(self, target_fps: float = 30.0):
        """
        Initialize the flawlessness analyzer.

        Args:
            target_fps: Expected frames per second of video
        """
        self.target_fps = target_fps

    def analyze(self, frame_scores: List[float],
                frame_angles: List[Dict[str, Optional[float]]],
                movement_name: str = "Unknown") -> FlawlessnessBreakdown:
        """
        Perform comprehensive flawlessness analysis.

        Args:
            frame_scores: List of per-frame scores (0-10)
            frame_angles: List of angle dictionaries per frame
            movement_name: Name of the movement being analyzed

        Returns:
            FlawlessnessBreakdown with detailed scores
        """
        if not frame_scores or not frame_angles:
            return FlawlessnessBreakdown(
                feedback=["No frames to analyze"]
            )

        # Calculate each component
        technical = self._calculate_technical_accuracy(frame_scores)
        consistency = self._calculate_consistency(frame_scores)
        fluidity = self._calculate_fluidity(frame_angles)
        timing = self._calculate_timing(frame_scores)
        completeness = self._calculate_completeness(frame_scores, frame_angles)

        # Calculate weighted overall score
        overall = (
            technical * self.WEIGHT_TECHNICAL +
            consistency * self.WEIGHT_CONSISTENCY +
            fluidity * self.WEIGHT_FLUIDITY +
            timing * self.WEIGHT_TIMING +
            completeness * self.WEIGHT_COMPLETENESS
        )

        # Determine level
        level = self._get_level(overall)

        # Generate feedback
        feedback = self._generate_feedback(
            movement_name, technical, consistency, fluidity, timing, completeness
        )

        return FlawlessnessBreakdown(
            technical_accuracy=technical,
            consistency=consistency,
            fluidity=fluidity,
            timing=timing,
            completeness=completeness,
            overall_score=overall,
            level=level,
            feedback=feedback
        )

    def _calculate_technical_accuracy(self, frame_scores: List[float]) -> float:
        """
        Calculate technical accuracy from frame scores.

        Technical accuracy = average score converted to 0-100 scale
        Bonus for peak scores above 9
        """
        if not frame_scores:
            return 0.0

        # Convert 0-10 scores to 0-100
        avg_score = np.mean(frame_scores) * 10

        # Bonus for excellent peak scores
        peak_score = max(frame_scores)
        if peak_score >= 9.0:
            avg_score = min(100, avg_score + 5)
        elif peak_score >= 8.0:
            avg_score = min(100, avg_score + 2)

        return avg_score

    def _calculate_consistency(self, frame_scores: List[float]) -> float:
        """
        Calculate consistency - how stable the form is.

        Lower variance = higher consistency score
        """
        if len(frame_scores) < 2:
            return 50.0  # Not enough data

        # Calculate coefficient of variation
        mean_score = np.mean(frame_scores)
        if mean_score == 0:
            return 0.0

        std_score = np.std(frame_scores)
        cv = std_score / mean_score

        # Convert to 0-100 scale (lower CV = higher consistency)
        # CV of 0 = 100% consistent
        # CV of 0.5 or higher = very inconsistent
        consistency = max(0, 100 - (cv * 200))

        return consistency

    def _calculate_fluidity(self, frame_angles: List[Dict[str, Optional[float]]]) -> float:
        """
        Calculate fluidity - smoothness of motion.

        Analyzes angle changes between frames.
        Jerky motion = large sudden changes = lower fluidity
        """
        if len(frame_angles) < 3:
            return 50.0  # Not enough data

        jerkiness_scores = []

        # Analyze each joint's motion
        for joint in ['left_knee', 'right_knee', 'left_hip', 'right_hip', 'spine']:
            angles = []
            for frame in frame_angles:
                if frame and joint in frame and frame[joint] is not None:
                    angles.append(frame[joint])

            if len(angles) >= 3:
                # Calculate second derivative (acceleration/jerk)
                first_diff = np.diff(angles)
                second_diff = np.diff(first_diff)

                # Large second derivatives indicate jerky motion
                avg_jerk = np.mean(np.abs(second_diff))

                # Convert to score (lower jerk = higher fluidity)
                # Jerk of 0 = 100, jerk of 20+ = 0
                joint_fluidity = max(0, 100 - (avg_jerk * 5))
                jerkiness_scores.append(joint_fluidity)

        if not jerkiness_scores:
            return 50.0

        return np.mean(jerkiness_scores)

    def _calculate_timing(self, frame_scores: List[float]) -> float:
        """
        Calculate timing - appropriate speed and rhythm.

        Looks for clear peak in scores (climax of movement)
        and appropriate build-up and wind-down.
        """
        if len(frame_scores) < 5:
            return 50.0  # Not enough data

        # Find peak
        peak_idx = np.argmax(frame_scores)
        peak_score = frame_scores[peak_idx]

        timing_score = 50.0  # Base score

        # Good timing: peak somewhere in middle (not at very start or end)
        relative_peak_pos = peak_idx / len(frame_scores)
        if 0.2 <= relative_peak_pos <= 0.8:
            timing_score += 20  # Peak in reasonable position

        # Good timing: scores build up to peak
        if peak_idx > 0:
            pre_peak = frame_scores[:peak_idx]
            if len(pre_peak) >= 2:
                # Check for increasing trend
                trend = np.polyfit(range(len(pre_peak)), pre_peak, 1)[0]
                if trend > 0:
                    timing_score += 15  # Good build-up

        # Good timing: clean descent from peak
        if peak_idx < len(frame_scores) - 1:
            post_peak = frame_scores[peak_idx:]
            if len(post_peak) >= 2:
                # Gradual descent is OK, not too abrupt
                timing_score += 15  # Some recovery phase

        return min(100, timing_score)

    def _calculate_completeness(self, frame_scores: List[float],
                                frame_angles: List[Dict[str, Optional[float]]]) -> float:
        """
        Calculate completeness - all phases of movement executed.

        Checks for:
        - Sufficient number of frames
        - Pose detected throughout
        - Score variation indicating movement phases
        """
        if not frame_scores:
            return 0.0

        completeness = 0.0

        # Check 1: Enough frames analyzed
        if len(frame_scores) >= 15:  # ~0.5 seconds at 30fps
            completeness += 30
        elif len(frame_scores) >= 10:
            completeness += 20
        elif len(frame_scores) >= 5:
            completeness += 10

        # Check 2: High pose detection rate
        valid_angles = sum(1 for fa in frame_angles if fa and any(v is not None for v in fa.values()))
        detection_rate = valid_angles / len(frame_angles) if frame_angles else 0
        completeness += detection_rate * 40

        # Check 3: Score variation (indicates movement, not static pose)
        if len(frame_scores) >= 3:
            score_range = max(frame_scores) - min(frame_scores)
            if score_range >= 2:  # Significant variation
                completeness += 30
            elif score_range >= 1:
                completeness += 20
            elif score_range >= 0.5:
                completeness += 10

        return min(100, completeness)

    def _get_level(self, score: float) -> FlawlessnessLevel:
        """Convert numeric score to flawlessness level."""
        if score >= 95:
            return FlawlessnessLevel.FLAWLESS
        elif score >= 85:
            return FlawlessnessLevel.EXCELLENT
        elif score >= 75:
            return FlawlessnessLevel.VERY_GOOD
        elif score >= 65:
            return FlawlessnessLevel.GOOD
        elif score >= 50:
            return FlawlessnessLevel.FAIR
        elif score >= 35:
            return FlawlessnessLevel.NEEDS_WORK
        else:
            return FlawlessnessLevel.POOR

    def _generate_feedback(self, movement_name: str,
                          technical: float, consistency: float,
                          fluidity: float, timing: float,
                          completeness: float) -> List[str]:
        """Generate specific feedback based on scores."""
        feedback = []

        # Technical feedback
        if technical >= 90:
            feedback.append(f"Excellent {movement_name} technique - angles are near-perfect")
        elif technical >= 70:
            feedback.append(f"Good {movement_name} technique - minor angle adjustments needed")
        elif technical >= 50:
            feedback.append(f"Fair technique - focus on key angles for {movement_name}")
        else:
            feedback.append(f"Technical form needs work - review proper {movement_name} angles")

        # Consistency feedback
        if consistency >= 80:
            feedback.append("Very consistent form throughout the movement")
        elif consistency >= 60:
            feedback.append("Mostly consistent - some variation in form")
        else:
            feedback.append("Inconsistent form - work on maintaining angles throughout")

        # Fluidity feedback
        if fluidity >= 80:
            feedback.append("Smooth, fluid motion")
        elif fluidity >= 60:
            feedback.append("Generally smooth with some jerky moments")
        else:
            feedback.append("Motion is jerky - practice slow, controlled movements")

        # Timing feedback
        if timing >= 80:
            feedback.append("Excellent timing and rhythm")
        elif timing >= 60:
            feedback.append("Good timing - clear movement phases")
        else:
            feedback.append("Work on timing - movement should have clear build-up and peak")

        # Completeness feedback
        if completeness >= 80:
            feedback.append("Complete movement execution")
        elif completeness >= 60:
            feedback.append("Most phases executed - ensure full completion")
        else:
            feedback.append("Movement appears incomplete - execute all phases")

        return feedback

    @staticmethod
    def get_level_color(level: FlawlessnessLevel) -> Tuple[int, int, int]:
        """Get RGB color for a flawlessness level."""
        colors = {
            FlawlessnessLevel.FLAWLESS: (255, 215, 0),    # Gold
            FlawlessnessLevel.EXCELLENT: (0, 255, 0),      # Green
            FlawlessnessLevel.VERY_GOOD: (50, 205, 50),    # Lime green
            FlawlessnessLevel.GOOD: (144, 238, 144),       # Light green
            FlawlessnessLevel.FAIR: (255, 255, 0),         # Yellow
            FlawlessnessLevel.NEEDS_WORK: (255, 165, 0),   # Orange
            FlawlessnessLevel.POOR: (255, 0, 0),           # Red
        }
        return colors.get(level, (128, 128, 128))

    @staticmethod
    def get_level_emoji(level: FlawlessnessLevel) -> str:
        """Get emoji for a flawlessness level."""
        emojis = {
            FlawlessnessLevel.FLAWLESS: "🏆",
            FlawlessnessLevel.EXCELLENT: "⭐",
            FlawlessnessLevel.VERY_GOOD: "✨",
            FlawlessnessLevel.GOOD: "👍",
            FlawlessnessLevel.FAIR: "📈",
            FlawlessnessLevel.NEEDS_WORK: "💪",
            FlawlessnessLevel.POOR: "📚",
        }
        return emojis.get(level, "")


def analyze_flawlessness(frame_scores: List[float],
                         frame_angles: List[Dict[str, Optional[float]]],
                         movement_name: str = "Unknown") -> FlawlessnessBreakdown:
    """
    Convenience function to analyze movement flawlessness.

    Args:
        frame_scores: List of per-frame scores (0-10)
        frame_angles: List of angle dictionaries per frame
        movement_name: Name of the movement

    Returns:
        FlawlessnessBreakdown with detailed analysis
    """
    analyzer = FlawlessnessAnalyzer()
    return analyzer.analyze(frame_scores, frame_angles, movement_name)
