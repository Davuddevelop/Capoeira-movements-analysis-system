"""
Report Generator Module

This module generates visual reports for capoeira movement analysis.
Reports include:
- Athlete information
- Scores per movement with color coding
- Frame-by-frame angle graphs
- Specific feedback and recommendations
- Overall session summary

Reports can be generated in HTML or PDF format.
"""

import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import numpy as np
from dataclasses import dataclass, field

# For PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus import Image as RLImage, PageBreak
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# For graph generation
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


@dataclass
class AthleteInfo:
    """Information about the athlete being analyzed."""
    name: str
    date: str = ""
    session_id: str = ""
    notes: str = ""

    def __post_init__(self):
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if not self.session_id:
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")


@dataclass
class MovementResult:
    """Results for a single movement analysis."""
    movement_name: str
    overall_score: float
    peak_score: float = 0.0
    lowest_score: float = 10.0
    average_score: float = 0.0
    frames_analyzed: int = 0
    frames_with_pose: int = 0
    feedback: List[str] = field(default_factory=list)
    frame_scores: List[float] = field(default_factory=list)
    angle_data: Dict[str, List[float]] = field(default_factory=dict)


@dataclass
class SessionReport:
    """Complete report for an analysis session."""
    athlete: AthleteInfo
    video_path: str
    video_duration: float
    total_frames: int
    movements: List[MovementResult] = field(default_factory=list)
    overall_score: float = 0.0
    detection_rate: float = 0.0
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ReportGenerator:
    """
    Generates analysis reports in various formats.

    This class takes movement analysis results and creates visual reports
    with scores, graphs, and feedback for athletes and coaches.
    """

    def __init__(self, output_dir: str = "output/reports"):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_score_color(self, score: float) -> str:
        """Get CSS/HTML color for a score."""
        if score >= 7:
            return "#28a745"  # Green
        elif score >= 5:
            return "#ffc107"  # Yellow/Orange
        else:
            return "#dc3545"  # Red

    def _get_score_label(self, score: float) -> str:
        """Get text label for a score."""
        if score >= 9:
            return "Excellent"
        elif score >= 7:
            return "Good"
        elif score >= 5:
            return "Fair"
        elif score >= 3:
            return "Needs Work"
        else:
            return "Poor"

    def generate_text_report(self, session: SessionReport) -> str:
        """
        Generate a simple text report.

        Args:
            session: SessionReport with analysis results

        Returns:
            Formatted text report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("CAPOEIRA MOVEMENT ANALYSIS REPORT")
        lines.append("Azerbaijan Capoeira Federation")
        lines.append("=" * 60)
        lines.append("")

        # Athlete info
        lines.append("ATHLETE INFORMATION")
        lines.append("-" * 40)
        lines.append(f"Name: {session.athlete.name}")
        lines.append(f"Date: {session.athlete.date}")
        lines.append(f"Session ID: {session.athlete.session_id}")
        if session.athlete.notes:
            lines.append(f"Notes: {session.athlete.notes}")
        lines.append("")

        # Video info
        lines.append("VIDEO INFORMATION")
        lines.append("-" * 40)
        lines.append(f"File: {Path(session.video_path).name}")
        lines.append(f"Duration: {session.video_duration:.2f} seconds")
        lines.append(f"Total Frames: {session.total_frames}")
        lines.append(f"Pose Detection Rate: {session.detection_rate:.1f}%")
        lines.append("")

        # Overall score
        lines.append("OVERALL SCORE")
        lines.append("-" * 40)
        lines.append(f"Score: {session.overall_score:.1f}/10 ({self._get_score_label(session.overall_score)})")
        lines.append("")

        # Movement scores
        lines.append("MOVEMENT SCORES")
        lines.append("-" * 40)
        for movement in session.movements:
            label = self._get_score_label(movement.overall_score)
            lines.append(f"\n{movement.movement_name}:")
            lines.append(f"  Score: {movement.overall_score:.1f}/10 ({label})")
            lines.append(f"  Peak: {movement.peak_score:.1f}/10")
            lines.append(f"  Lowest: {movement.lowest_score:.1f}/10")
            lines.append(f"  Frames: {movement.frames_with_pose}/{movement.frames_analyzed}")

            if movement.feedback:
                lines.append("  Feedback:")
                for fb in movement.feedback[:5]:  # Top 5 feedback items
                    lines.append(f"    - {fb}")
        lines.append("")

        # Footer
        lines.append("=" * 60)
        lines.append(f"Report generated: {session.generated_at}")
        lines.append("Powered by Capoeira Movement Analysis System")
        lines.append("=" * 60)

        return "\n".join(lines)

    def generate_html_report(self, session: SessionReport,
                            include_graphs: bool = True) -> str:
        """
        Generate an HTML report with styling.

        Args:
            session: SessionReport with analysis results
            include_graphs: Whether to include graph images

        Returns:
            HTML report string
        """
        html = []

        # HTML header
        html.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Capoeira Movement Analysis Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #1a5f2a 0%, #2d8a3e 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #1a5f2a;
            border-bottom: 2px solid #1a5f2a;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .score-card {
            display: inline-block;
            padding: 20px 40px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
        .score-excellent { background-color: #28a745; }
        .score-good { background-color: #28a745; }
        .score-fair { background-color: #ffc107; color: #333; }
        .score-needs-work { background-color: #dc3545; }
        .score-poor { background-color: #dc3545; }
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .info-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .info-label {
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
        }
        .info-value {
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }
        .movement-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .movement-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .movement-name {
            font-size: 20px;
            font-weight: bold;
        }
        .movement-score {
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
        }
        .feedback-list {
            margin: 0;
            padding-left: 20px;
        }
        .feedback-list li {
            margin-bottom: 5px;
        }
        .footer {
            text-align: center;
            color: #666;
            padding: 20px;
            font-size: 14px;
        }
        .graph-container {
            text-align: center;
            margin: 20px 0;
        }
        .graph-container img {
            max-width: 100%;
            border-radius: 5px;
        }
    </style>
</head>
<body>
""")

        # Header
        html.append(f"""
    <div class="header">
        <h1>Capoeira Movement Analysis Report</h1>
        <p>Azerbaijan Capoeira Federation</p>
    </div>
""")

        # Athlete info section
        html.append(f"""
    <div class="section">
        <h2>Athlete Information</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Athlete Name</div>
                <div class="info-value">{session.athlete.name}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Date</div>
                <div class="info-value">{session.athlete.date}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Session ID</div>
                <div class="info-value">{session.athlete.session_id}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Video Duration</div>
                <div class="info-value">{session.video_duration:.2f} seconds</div>
            </div>
        </div>
    </div>
""")

        # Overall score section
        score_class = self._get_score_label(session.overall_score).lower().replace(" ", "-")
        html.append(f"""
    <div class="section" style="text-align: center;">
        <h2>Overall Score</h2>
        <div class="score-card score-{score_class}">
            {session.overall_score:.1f}/10
            <br>
            <span style="font-size: 16px;">{self._get_score_label(session.overall_score)}</span>
        </div>
        <p style="margin-top: 15px;">
            Pose Detection Rate: {session.detection_rate:.1f}%
            ({session.total_frames} frames analyzed)
        </p>
    </div>
""")

        # Movement scores section
        html.append("""
    <div class="section">
        <h2>Movement Scores</h2>
""")

        for movement in session.movements:
            score_color = self._get_score_color(movement.overall_score)
            html.append(f"""
        <div class="movement-card">
            <div class="movement-header">
                <span class="movement-name">{movement.movement_name}</span>
                <span class="movement-score" style="background-color: {score_color};">
                    {movement.overall_score:.1f}/10
                </span>
            </div>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Peak Score</div>
                    <div class="info-value">{movement.peak_score:.1f}/10</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Average Score</div>
                    <div class="info-value">{movement.average_score:.1f}/10</div>
                </div>
            </div>
""")

            if movement.feedback:
                html.append("""
            <h4 style="margin-bottom: 5px;">Feedback:</h4>
            <ul class="feedback-list">
""")
                for fb in movement.feedback[:5]:
                    html.append(f"                <li>{fb}</li>\n")
                html.append("            </ul>\n")

            html.append("        </div>\n")

        html.append("    </div>\n")

        # Footer
        html.append(f"""
    <div class="footer">
        <p>Report generated: {session.generated_at}</p>
        <p>Powered by Capoeira Movement Analysis System</p>
    </div>
</body>
</html>
""")

        return "".join(html)

    def save_text_report(self, session: SessionReport, filename: str = None) -> str:
        """
        Save a text report to file.

        Args:
            session: SessionReport with analysis results
            filename: Optional custom filename

        Returns:
            Path to the saved report
        """
        if filename is None:
            filename = f"report_{session.athlete.session_id}.txt"

        filepath = self.output_dir / filename
        content = self.generate_text_report(session)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def save_html_report(self, session: SessionReport, filename: str = None) -> str:
        """
        Save an HTML report to file.

        Args:
            session: SessionReport with analysis results
            filename: Optional custom filename

        Returns:
            Path to the saved report
        """
        if filename is None:
            filename = f"report_{session.athlete.session_id}.html"

        filepath = self.output_dir / filename
        content = self.generate_html_report(session)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def generate_angle_graph(self, movement: MovementResult,
                            output_path: str = None) -> Optional[str]:
        """
        Generate a graph showing angle changes over time.

        Args:
            movement: MovementResult with angle data
            output_path: Path to save the graph image

        Returns:
            Path to saved graph or None if matplotlib not available
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        if not movement.angle_data:
            return None

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"{movement.movement_name} - Joint Angles Over Time", fontsize=14)

        angle_groups = [
            (['left_knee', 'right_knee'], 'Knee Angles'),
            (['left_hip', 'right_hip'], 'Hip Angles'),
            (['left_elbow', 'right_elbow'], 'Elbow Angles'),
            (['spine'], 'Spine Angle'),
        ]

        for idx, (angle_keys, title) in enumerate(angle_groups):
            ax = axes[idx // 2, idx % 2]
            ax.set_title(title)
            ax.set_xlabel('Frame')
            ax.set_ylabel('Angle (degrees)')

            for key in angle_keys:
                if key in movement.angle_data:
                    data = movement.angle_data[key]
                    frames = range(len(data))
                    ax.plot(frames, data, label=key.replace('_', ' ').title())

            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path is None:
            output_path = self.output_dir / f"graph_{movement.movement_name.lower()}.png"

        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def generate_score_graph(self, movement: MovementResult,
                            output_path: str = None) -> Optional[str]:
        """
        Generate a graph showing score changes over time.

        Args:
            movement: MovementResult with frame scores
            output_path: Path to save the graph image

        Returns:
            Path to saved graph or None if matplotlib not available
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        if not movement.frame_scores:
            return None

        fig, ax = plt.subplots(figsize=(10, 4))

        frames = range(len(movement.frame_scores))
        scores = movement.frame_scores

        # Color code the line based on score
        colors = [self._get_score_color(s) for s in scores]

        ax.plot(frames, scores, 'b-', alpha=0.5)
        ax.scatter(frames, scores, c=colors, s=10)

        # Add horizontal lines for score thresholds
        ax.axhline(y=7, color='green', linestyle='--', alpha=0.5, label='Good (7)')
        ax.axhline(y=5, color='orange', linestyle='--', alpha=0.5, label='Fair (5)')

        ax.set_title(f"{movement.movement_name} - Score Over Time")
        ax.set_xlabel('Frame')
        ax.set_ylabel('Score (0-10)')
        ax.set_ylim(0, 10.5)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path is None:
            output_path = self.output_dir / f"scores_{movement.movement_name.lower()}.png"

        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()

        return str(output_path)


def create_sample_report() -> SessionReport:
    """
    Create a sample report for testing purposes.

    Returns:
        A SessionReport with dummy data
    """
    athlete = AthleteInfo(
        name="Test Athlete",
        notes="Sample report for testing"
    )

    ginga_result = MovementResult(
        movement_name="Ginga",
        overall_score=7.5,
        peak_score=9.0,
        lowest_score=5.5,
        average_score=7.5,
        frames_analyzed=150,
        frames_with_pose=145,
        feedback=[
            "Good knee bend maintained throughout",
            "Consider keeping spine slightly more upright",
            "Good rhythm consistency"
        ],
        frame_scores=[7.0, 7.5, 8.0, 7.5, 8.5, 7.0, 6.5, 7.0, 7.5, 8.0]
    )

    session = SessionReport(
        athlete=athlete,
        video_path="sample_video.mp4",
        video_duration=5.0,
        total_frames=150,
        movements=[ginga_result],
        overall_score=7.5,
        detection_rate=96.7
    )

    return session
