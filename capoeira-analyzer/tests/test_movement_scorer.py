"""
Tests for the MovementScorer module.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.movement_scorer import (
    MovementScorer, AngleCriterion, FrameScore, MovementScore,
    ScoreLevel, create_criterion, GenericMovementScorer
)


class TestAngleCriterion:
    """Tests for AngleCriterion class."""

    def test_is_calibrated_false(self):
        """Test uncalibrated criterion."""
        criterion = AngleCriterion(
            name="Test",
            angle_key="left_knee",
            ideal_min=None,
            ideal_max=None
        )
        assert criterion.is_calibrated() is False

    def test_is_calibrated_true(self):
        """Test calibrated criterion."""
        criterion = AngleCriterion(
            name="Test",
            angle_key="left_knee",
            ideal_min=120,
            ideal_max=160
        )
        assert criterion.is_calibrated() is True

    def test_score_angle_uncalibrated(self):
        """Test scoring with uncalibrated criterion."""
        criterion = AngleCriterion(
            name="Test",
            angle_key="left_knee"
        )
        score, feedback = criterion.score_angle(140)
        assert score == 5.0  # Default score for uncalibrated
        assert "not yet calibrated" in feedback

    def test_score_angle_in_range(self):
        """Test scoring when angle is in ideal range."""
        criterion = AngleCriterion(
            name="Test",
            angle_key="left_knee",
            ideal_min=120,
            ideal_max=160
        )
        score, feedback = criterion.score_angle(140)
        assert score == 10.0
        assert "Excellent" in feedback

    def test_score_angle_out_of_range(self):
        """Test scoring when angle is out of range."""
        criterion = AngleCriterion(
            name="Test",
            angle_key="left_knee",
            ideal_min=120,
            ideal_max=160
        )
        score, feedback = criterion.score_angle(100)  # Below range
        assert score < 10.0
        assert "too low" in feedback

    def test_score_angle_none(self):
        """Test scoring with None angle (not visible)."""
        criterion = AngleCriterion(
            name="Test",
            angle_key="left_knee",
            ideal_min=120,
            ideal_max=160
        )
        score, feedback = criterion.score_angle(None)
        assert score == 0.0
        assert "not visible" in feedback


class TestScoreLevel:
    """Tests for ScoreLevel enum."""

    def test_score_level_values(self):
        """Test that all score levels are defined."""
        assert ScoreLevel.EXCELLENT.value == "excellent"
        assert ScoreLevel.GOOD.value == "good"
        assert ScoreLevel.FAIR.value == "fair"
        assert ScoreLevel.NEEDS_WORK.value == "needs_work"
        assert ScoreLevel.POOR.value == "poor"


class TestMovementScorer:
    """Tests for MovementScorer base class."""

    def test_get_score_level_excellent(self):
        """Test score level for excellent score."""
        assert MovementScorer.get_score_level(9.5) == ScoreLevel.EXCELLENT
        assert MovementScorer.get_score_level(10.0) == ScoreLevel.EXCELLENT

    def test_get_score_level_good(self):
        """Test score level for good score."""
        assert MovementScorer.get_score_level(7.0) == ScoreLevel.GOOD
        assert MovementScorer.get_score_level(8.9) == ScoreLevel.GOOD

    def test_get_score_level_fair(self):
        """Test score level for fair score."""
        assert MovementScorer.get_score_level(5.0) == ScoreLevel.FAIR
        assert MovementScorer.get_score_level(6.9) == ScoreLevel.FAIR

    def test_get_score_level_needs_work(self):
        """Test score level for needs work score."""
        assert MovementScorer.get_score_level(3.0) == ScoreLevel.NEEDS_WORK
        assert MovementScorer.get_score_level(4.9) == ScoreLevel.NEEDS_WORK

    def test_get_score_level_poor(self):
        """Test score level for poor score."""
        assert MovementScorer.get_score_level(0.0) == ScoreLevel.POOR
        assert MovementScorer.get_score_level(2.9) == ScoreLevel.POOR

    def test_get_score_color(self):
        """Test score color coding."""
        assert MovementScorer.get_score_color(8.0) == (0, 255, 0)  # Green
        assert MovementScorer.get_score_color(6.0) == (255, 255, 0)  # Yellow
        assert MovementScorer.get_score_color(3.0) == (255, 0, 0)  # Red


class TestGenericMovementScorer:
    """Tests for GenericMovementScorer."""

    def test_generic_scorer_creation(self):
        """Test creating a generic scorer."""
        scorer = GenericMovementScorer()
        assert scorer.movement_name == "Generic Movement"
        assert scorer.criteria == []

    def test_generic_scorer_is_not_calibrated(self):
        """Test that generic scorer is not calibrated."""
        scorer = GenericMovementScorer()
        assert scorer.is_calibrated() is False


class TestCreateCriterion:
    """Tests for create_criterion factory function."""

    def test_create_criterion_basic(self):
        """Test basic criterion creation."""
        criterion = create_criterion(
            name="Test Criterion",
            angle_key="left_knee",
            weight=0.8,
            description="A test criterion"
        )
        assert criterion.name == "Test Criterion"
        assert criterion.angle_key == "left_knee"
        assert criterion.weight == 0.8
        assert criterion.ideal_min is None
        assert criterion.ideal_max is None

    def test_create_criterion_calibrated(self):
        """Test calibrated criterion creation."""
        criterion = create_criterion(
            name="Test Criterion",
            angle_key="left_knee",
            ideal_min=90,
            ideal_max=180,
            weight=1.0
        )
        assert criterion.is_calibrated() is True
