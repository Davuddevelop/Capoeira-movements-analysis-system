"""
Tests for the ReportGenerator module.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.report_generator import (
    ReportGenerator, SessionReport, AthleteInfo, MovementResult,
    create_sample_report
)


class TestAthleteInfo:
    """Tests for AthleteInfo dataclass."""

    def test_athlete_info_creation(self):
        """Test creating athlete info."""
        athlete = AthleteInfo(name="Test Athlete")
        assert athlete.name == "Test Athlete"
        assert athlete.date != ""  # Should have auto-generated date
        assert athlete.session_id != ""  # Should have auto-generated session ID

    def test_athlete_info_with_notes(self):
        """Test athlete info with notes."""
        athlete = AthleteInfo(name="Test", notes="Some notes")
        assert athlete.notes == "Some notes"


class TestMovementResult:
    """Tests for MovementResult dataclass."""

    def test_movement_result_creation(self):
        """Test creating movement result."""
        result = MovementResult(
            movement_name="Ginga",
            overall_score=7.5
        )
        assert result.movement_name == "Ginga"
        assert result.overall_score == 7.5
        assert result.peak_score == 0.0  # Default
        assert result.feedback == []  # Default empty list


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()

    def test_get_score_color_green(self):
        """Test green color for high scores."""
        color = self.generator._get_score_color(8.0)
        assert color == "#28a745"

    def test_get_score_color_yellow(self):
        """Test yellow color for medium scores."""
        color = self.generator._get_score_color(6.0)
        assert color == "#ffc107"

    def test_get_score_color_red(self):
        """Test red color for low scores."""
        color = self.generator._get_score_color(3.0)
        assert color == "#dc3545"

    def test_get_score_label_excellent(self):
        """Test excellent label."""
        label = self.generator._get_score_label(9.5)
        assert label == "Excellent"

    def test_get_score_label_good(self):
        """Test good label."""
        label = self.generator._get_score_label(7.5)
        assert label == "Good"

    def test_get_score_label_fair(self):
        """Test fair label."""
        label = self.generator._get_score_label(5.5)
        assert label == "Fair"

    def test_get_score_label_needs_work(self):
        """Test needs work label."""
        label = self.generator._get_score_label(3.5)
        assert label == "Needs Work"

    def test_get_score_label_poor(self):
        """Test poor label."""
        label = self.generator._get_score_label(1.5)
        assert label == "Poor"


class TestCreateSampleReport:
    """Tests for sample report creation."""

    def test_create_sample_report(self):
        """Test creating a sample report."""
        report = create_sample_report()
        assert report.athlete.name == "Test Athlete"
        assert len(report.movements) > 0
        assert report.overall_score > 0


class TestTextReportGeneration:
    """Tests for text report generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.sample_report = create_sample_report()

    def test_generate_text_report(self):
        """Test generating a text report."""
        text = self.generator.generate_text_report(self.sample_report)
        assert "CAPOEIRA MOVEMENT ANALYSIS REPORT" in text
        assert self.sample_report.athlete.name in text
        assert "Azerbaijan Capoeira Federation" in text

    def test_text_report_contains_scores(self):
        """Test that text report contains movement scores."""
        text = self.generator.generate_text_report(self.sample_report)
        assert "MOVEMENT SCORES" in text
        for movement in self.sample_report.movements:
            assert movement.movement_name in text


class TestHtmlReportGeneration:
    """Tests for HTML report generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.sample_report = create_sample_report()

    def test_generate_html_report(self):
        """Test generating an HTML report."""
        html = self.generator.generate_html_report(self.sample_report)
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html

    def test_html_report_contains_athlete(self):
        """Test that HTML report contains athlete info."""
        html = self.generator.generate_html_report(self.sample_report)
        assert self.sample_report.athlete.name in html

    def test_html_report_has_styles(self):
        """Test that HTML report has CSS styles."""
        html = self.generator.generate_html_report(self.sample_report)
        assert "<style>" in html
        assert "font-family" in html
