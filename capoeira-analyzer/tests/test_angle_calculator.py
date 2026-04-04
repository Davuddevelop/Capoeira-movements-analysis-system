"""
Tests for the AngleCalculator module.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.angle_calculator import AngleCalculator, quick_angle


class TestAngleCalculator:
    """Tests for AngleCalculator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calc = AngleCalculator()

    def test_calculate_angle_right_angle(self):
        """Test calculation of a 90-degree angle."""
        # Points forming a right angle: A at (0,0), B at (1,0), C at (1,1)
        angle = self.calc.calculate_angle((0, 0), (1, 0), (1, 1))
        assert 85 < angle < 95, f"Expected ~90°, got {angle}°"

    def test_calculate_angle_straight_line(self):
        """Test calculation of a straight line (180 degrees)."""
        # Points in a straight line
        angle = self.calc.calculate_angle((0, 0), (1, 0), (2, 0))
        assert 175 < angle < 185, f"Expected ~180°, got {angle}°"

    def test_calculate_angle_obtuse(self):
        """Test calculation of an obtuse angle (~135 degrees)."""
        # Points: A at (0,0), B at (1,0), C at (2,1) forms 135 degree angle at B
        angle = self.calc.calculate_angle((0, 0), (1, 0), (2, 1))
        assert 130 < angle < 140, f"Expected ~135°, got {angle}°"

    def test_calculate_angle_3d_right_angle(self):
        """Test 3D angle calculation."""
        angle = self.calc.calculate_angle_3d((0, 0, 0), (1, 0, 0), (1, 1, 0))
        assert 85 < angle < 95, f"Expected ~90°, got {angle}°"

    def test_quick_angle_function(self):
        """Test the quick_angle utility function."""
        angle = quick_angle((0, 0), (1, 0), (1, 1))
        assert 85 < angle < 95, f"Expected ~90°, got {angle}°"

    def test_landmark_indices(self):
        """Test that landmark indices are defined correctly."""
        assert self.calc.LANDMARKS['left_knee'] == 25
        assert self.calc.LANDMARKS['right_knee'] == 26
        assert self.calc.LANDMARKS['left_hip'] == 23
        assert self.calc.LANDMARKS['right_hip'] == 24
        assert self.calc.LANDMARKS['left_shoulder'] == 11
        assert self.calc.LANDMARKS['right_shoulder'] == 12


class TestAngleCalculatorEdgeCases:
    """Test edge cases for AngleCalculator."""

    def setup_method(self):
        self.calc = AngleCalculator()

    def test_same_points(self):
        """Test with coincident points (should handle gracefully)."""
        # When all points are the same, result may be undefined
        # but shouldn't crash
        angle = self.calc.calculate_angle_3d((1, 1, 1), (1, 1, 1), (1, 1, 1))
        # Result might be 0 or NaN, but shouldn't raise exception
        assert angle >= 0 or angle != angle  # NaN check

    def test_visibility_threshold(self):
        """Test that visibility threshold is respected."""
        calc = AngleCalculator(min_visibility=0.8)
        assert calc.min_visibility == 0.8
