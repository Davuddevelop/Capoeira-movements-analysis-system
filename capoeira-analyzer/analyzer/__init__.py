"""
Capoeira Analyzer - Core Analysis Module

This module contains the core components for analyzing capoeira movements:
- pose_detector: MediaPipe pose detection
- angle_calculator: Joint angle calculations
- movement_scorer: Base scoring logic
- report_generator: Visual report generation
- flawlessness: Advanced flawlessness rating system
- movement_detector: Automatic movement identification
- combination_analyzer: Movement sequence/flow analysis

Azerbaijan Capoeira Federation Project
"""

from .pose_detector import PoseDetector
from .angle_calculator import AngleCalculator
from .movement_scorer import MovementScorer
from .report_generator import ReportGenerator
from .flawlessness import FlawlessnessAnalyzer, FlawlessnessLevel, analyze_flawlessness
from .movement_detector import (
    MovementDetector,
    MovementCategory,
    DetectedMovement,
    BodyState,
    create_detector
)
from .combination_analyzer import (
    CombinationAnalyzer,
    CombinationLevel,
    CombinationResult,
    analyze_combination
)

__all__ = [
    'PoseDetector',
    'AngleCalculator',
    'MovementScorer',
    'ReportGenerator',
    'FlawlessnessAnalyzer',
    'FlawlessnessLevel',
    'analyze_flawlessness',
    'MovementDetector',
    'MovementCategory',
    'DetectedMovement',
    'BodyState',
    'create_detector',
    'CombinationAnalyzer',
    'CombinationLevel',
    'CombinationResult',
    'analyze_combination',
]
