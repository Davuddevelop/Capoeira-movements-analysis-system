"""
Movement Scorer Module

This module provides the base class for scoring capoeira movements.
Each specific movement (Ginga, Au, etc.) extends this class to implement
its own scoring criteria.

The scoring is based on comparing detected joint angles against ideal
angle ranges defined by capoeira coaches/experts.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class ScoreLevel(Enum):
    """Score level categories for visual feedback."""
    EXCELLENT = "excellent"  # 9-10
    GOOD = "good"            # 7-8
    FAIR = "fair"            # 5-6
    NEEDS_WORK = "needs_work"  # 3-4
    POOR = "poor"            # 0-2


@dataclass
class AngleCriterion:
    """
    Defines a scoring criterion based on a joint angle.

    Attributes:
        name: Human-readable name of the criterion
        angle_key: Key to look up in the angles dictionary
        ideal_min: Minimum ideal angle (None = to be calibrated)
        ideal_max: Maximum ideal angle (None = to be calibrated)
        weight: Importance weight for this criterion (0-1)
        description: Description of what this criterion measures
    """
    name: str
    angle_key: str
    ideal_min: Optional[float] = None  # To be calibrated with coach
    ideal_max: Optional[float] = None  # To be calibrated with coach
    weight: float = 1.0
    description: str = ""

    def is_calibrated(self) -> bool:
        """Check if this criterion has been calibrated with actual values."""
        return self.ideal_min is not None and self.ideal_max is not None

    def score_angle(self, angle: Optional[float]) -> Tuple[float, str]:
        """
        Score an angle against this criterion.

        Args:
            angle: The measured angle in degrees

        Returns:
            Tuple of (score 0-10, feedback message)
        """
        if angle is None:
            return 0.0, f"{self.name}: Angle not visible"

        if not self.is_calibrated():
            return 5.0, f"{self.name}: Criteria not yet calibrated (measured: {angle:.1f}°)"

        # Check if angle is within ideal range
        if self.ideal_min <= angle <= self.ideal_max:
            return 10.0, f"{self.name}: Excellent ({angle:.1f}° within {self.ideal_min}-{self.ideal_max}°)"

        # Calculate how far off the angle is
        if angle < self.ideal_min:
            deviation = self.ideal_min - angle
            direction = "too low"
        else:
            deviation = angle - self.ideal_max
            direction = "too high"

        # Score decreases based on deviation
        # Every 10 degrees off loses ~2 points
        score = max(0, 10 - (deviation / 5))

        feedback = f"{self.name}: {angle:.1f}° ({direction}, ideal: {self.ideal_min}-{self.ideal_max}°)"

        return score, feedback


@dataclass
class FrameScore:
    """Stores the score for a single frame."""
    frame_number: int
    timestamp: float
    overall_score: float
    criterion_scores: Dict[str, float] = field(default_factory=dict)
    feedback: List[str] = field(default_factory=list)
    angles: Dict[str, Optional[float]] = field(default_factory=dict)


@dataclass
class MovementScore:
    """Stores the overall score for a movement sequence."""
    movement_name: str
    overall_score: float
    frame_scores: List[FrameScore] = field(default_factory=list)
    peak_score: float = 0.0
    lowest_score: float = 10.0
    average_score: float = 0.0
    feedback_summary: List[str] = field(default_factory=list)
    frames_analyzed: int = 0
    frames_with_pose: int = 0


class MovementScorer(ABC):
    """
    Abstract base class for scoring capoeira movements.

    Each specific movement (Ginga, Au, Meia-lua, etc.) should extend this
    class and define its own criteria and scoring logic.

    Attributes:
        movement_name: Name of the movement being scored
        movement_name_pt: Portuguese name of the movement
        description: Description of the movement
        criteria: List of AngleCriterion objects defining scoring criteria
    """

    def __init__(self):
        """Initialize the movement scorer."""
        self.movement_name: str = "Unknown Movement"
        self.movement_name_pt: str = ""
        self.description: str = ""
        self.criteria: List[AngleCriterion] = []
        self.common_mistakes: List[str] = []

        # Call setup method to define movement-specific attributes
        self._setup()

    @abstractmethod
    def _setup(self):
        """
        Set up movement-specific attributes.

        Subclasses must override this to define:
        - movement_name
        - movement_name_pt
        - description
        - criteria (list of AngleCriterion)
        - common_mistakes
        """
        pass

    def score_frame(self, angles: Dict[str, Optional[float]],
                   frame_number: int = 0,
                   timestamp: float = 0.0) -> FrameScore:
        """
        Score a single frame based on joint angles.

        Args:
            angles: Dictionary of joint angles from AngleCalculator
            frame_number: The frame number being scored
            timestamp: Timestamp of the frame in seconds

        Returns:
            FrameScore object with scoring results
        """
        frame_score = FrameScore(
            frame_number=frame_number,
            timestamp=timestamp,
            overall_score=0.0,
            angles=angles.copy()
        )

        if not self.criteria:
            frame_score.feedback.append("No scoring criteria defined")
            return frame_score

        total_weight = 0
        weighted_score = 0

        for criterion in self.criteria:
            angle = angles.get(criterion.angle_key)
            score, feedback = criterion.score_angle(angle)

            frame_score.criterion_scores[criterion.name] = score
            frame_score.feedback.append(feedback)

            weighted_score += score * criterion.weight
            total_weight += criterion.weight

        # Calculate overall score
        if total_weight > 0:
            frame_score.overall_score = weighted_score / total_weight
        else:
            frame_score.overall_score = 0.0

        return frame_score

    def score_sequence(self, frames_angles: List[Dict[str, Optional[float]]],
                      timestamps: Optional[List[float]] = None) -> MovementScore:
        """
        Score a full movement sequence (multiple frames).

        Args:
            frames_angles: List of angle dictionaries, one per frame
            timestamps: Optional list of timestamps for each frame

        Returns:
            MovementScore object with overall scoring results
        """
        movement_score = MovementScore(
            movement_name=self.movement_name,
            overall_score=0.0,
            frames_analyzed=len(frames_angles)
        )

        if not frames_angles:
            movement_score.feedback_summary.append("No frames to analyze")
            return movement_score

        scores = []

        for i, angles in enumerate(frames_angles):
            timestamp = timestamps[i] if timestamps and i < len(timestamps) else i / 30.0

            frame_score = self.score_frame(angles, frame_number=i, timestamp=timestamp)
            movement_score.frame_scores.append(frame_score)

            if frame_score.overall_score > 0:
                scores.append(frame_score.overall_score)
                movement_score.frames_with_pose += 1

        if scores:
            movement_score.peak_score = max(scores)
            movement_score.lowest_score = min(scores)
            movement_score.average_score = np.mean(scores)
            movement_score.overall_score = movement_score.average_score

            # Generate feedback summary
            movement_score.feedback_summary = self._generate_feedback_summary(movement_score)

        return movement_score

    def _generate_feedback_summary(self, movement_score: MovementScore) -> List[str]:
        """
        Generate a summary of feedback for the movement.

        Args:
            movement_score: The MovementScore object with frame scores

        Returns:
            List of feedback strings
        """
        summary = []

        # Overall performance
        level = self.get_score_level(movement_score.overall_score)
        summary.append(f"Overall {self.movement_name} performance: {level.value.replace('_', ' ').title()}")
        summary.append(f"Average score: {movement_score.overall_score:.1f}/10")
        summary.append(f"Peak score: {movement_score.peak_score:.1f}/10")

        # Detection rate
        if movement_score.frames_analyzed > 0:
            detection_rate = movement_score.frames_with_pose / movement_score.frames_analyzed * 100
            summary.append(f"Pose detected in {detection_rate:.1f}% of frames")

        # Identify weak areas
        if movement_score.frame_scores:
            criterion_averages = {}
            for frame_score in movement_score.frame_scores:
                for name, score in frame_score.criterion_scores.items():
                    if name not in criterion_averages:
                        criterion_averages[name] = []
                    criterion_averages[name].append(score)

            weak_areas = []
            for name, scores in criterion_averages.items():
                avg = np.mean(scores)
                if avg < 6.0:
                    weak_areas.append(f"{name} (avg: {avg:.1f})")

            if weak_areas:
                summary.append("Areas needing improvement: " + ", ".join(weak_areas))

        # Add relevant common mistakes if score is low
        if movement_score.overall_score < 6.0 and self.common_mistakes:
            summary.append("Common mistakes to avoid:")
            for mistake in self.common_mistakes[:3]:  # Top 3 mistakes
                summary.append(f"  - {mistake}")

        return summary

    @staticmethod
    def get_score_level(score: float) -> ScoreLevel:
        """
        Get the score level category for a numeric score.

        Args:
            score: Score from 0-10

        Returns:
            ScoreLevel enum value
        """
        if score >= 9:
            return ScoreLevel.EXCELLENT
        elif score >= 7:
            return ScoreLevel.GOOD
        elif score >= 5:
            return ScoreLevel.FAIR
        elif score >= 3:
            return ScoreLevel.NEEDS_WORK
        else:
            return ScoreLevel.POOR

    @staticmethod
    def get_score_color(score: float) -> Tuple[int, int, int]:
        """
        Get the RGB color for a score (for visualization).

        Args:
            score: Score from 0-10

        Returns:
            RGB tuple (red, green, blue) with values 0-255
        """
        if score >= 7:
            return (0, 255, 0)  # Green
        elif score >= 5:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red

    def get_feedback(self, score: float) -> str:
        """
        Get text feedback based on the score.

        Args:
            score: Score from 0-10

        Returns:
            Feedback text string
        """
        level = self.get_score_level(score)

        feedback_map = {
            ScoreLevel.EXCELLENT: f"Excellent {self.movement_name}! Keep it up!",
            ScoreLevel.GOOD: f"Good {self.movement_name}. Minor adjustments can make it perfect.",
            ScoreLevel.FAIR: f"Fair {self.movement_name}. Focus on the key angles.",
            ScoreLevel.NEEDS_WORK: f"{self.movement_name} needs more practice. Review the criteria.",
            ScoreLevel.POOR: f"Keep practicing {self.movement_name}. Consider working with your coach."
        }

        return feedback_map.get(level, "Score calculated.")

    def is_calibrated(self) -> bool:
        """
        Check if all criteria have been calibrated.

        Returns:
            True if all criteria have ideal angle ranges defined
        """
        if not self.criteria:
            return False
        return all(criterion.is_calibrated() for criterion in self.criteria)

    def get_calibration_status(self) -> Dict[str, bool]:
        """
        Get calibration status for each criterion.

        Returns:
            Dictionary mapping criterion names to calibration status
        """
        return {
            criterion.name: criterion.is_calibrated()
            for criterion in self.criteria
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(movement='{self.movement_name}', criteria={len(self.criteria)})"


class GenericMovementScorer(MovementScorer):
    """
    A generic movement scorer that can be used for any movement.

    This is useful for testing or when you want to score without
    predefined criteria.
    """

    def _setup(self):
        self.movement_name = "Generic Movement"
        self.movement_name_pt = "Movimento Genérico"
        self.description = "A generic movement scorer for testing purposes."
        self.criteria = []
        self.common_mistakes = []


def create_criterion(name: str, angle_key: str,
                    ideal_min: Optional[float] = None,
                    ideal_max: Optional[float] = None,
                    weight: float = 1.0,
                    description: str = "") -> AngleCriterion:
    """
    Factory function to create an AngleCriterion.

    This is a convenience function that creates criteria with placeholder
    values that will be calibrated with the coach later.

    Args:
        name: Human-readable name
        angle_key: Key in the angles dictionary
        ideal_min: Minimum ideal angle (None if not calibrated)
        ideal_max: Maximum ideal angle (None if not calibrated)
        weight: Importance weight (0-1)
        description: What this criterion measures

    Returns:
        AngleCriterion object
    """
    return AngleCriterion(
        name=name,
        angle_key=angle_key,
        ideal_min=ideal_min,
        ideal_max=ideal_max,
        weight=weight,
        description=description
    )
