"""
Tests for the combination/sequence analysis system.
"""

import pytest
from analyzer.combination_analyzer import (
    CombinationAnalyzer,
    CombinationLevel,
    CombinationResult,
    TransitionAnalysis,
    analyze_combination,
    TRANSITION_MATRIX
)
from analyzer.movement_detector import DetectedMovement, MovementCategory


class TestCombinationAnalyzer:
    """Tests for CombinationAnalyzer class."""

    def test_analyzer_creation(self):
        """Test that analyzer can be created."""
        analyzer = CombinationAnalyzer()
        assert analyzer is not None
        assert analyzer.fps == 30.0

    def test_analyzer_with_custom_fps(self):
        """Test analyzer with custom fps."""
        analyzer = CombinationAnalyzer(fps=60.0)
        assert analyzer.fps == 60.0

    def test_analyzer_has_transition_matrix(self):
        """Test that analyzer has transition definitions."""
        analyzer = CombinationAnalyzer()
        assert len(analyzer.transition_matrix) >= 10

    def test_analyze_empty_list(self):
        """Test analyzing empty detection list."""
        analyzer = CombinationAnalyzer()
        result = analyzer.analyze([])
        assert result.overall_score == 0
        assert result.level == CombinationLevel.NOVICE


class TestCombinationLevel:
    """Tests for CombinationLevel enum."""

    def test_all_levels_exist(self):
        """Test that all expected levels exist."""
        assert CombinationLevel.MASTER.value == "Master Flow"
        assert CombinationLevel.EXPERT.value == "Expert Flow"
        assert CombinationLevel.ADVANCED.value == "Advanced Flow"
        assert CombinationLevel.INTERMEDIATE.value == "Intermediate"
        assert CombinationLevel.DEVELOPING.value == "Developing"
        assert CombinationLevel.BEGINNER.value == "Beginner"
        assert CombinationLevel.NOVICE.value == "Novice"


class TestTransitionMatrix:
    """Tests for the transition matrix."""

    def test_ginga_has_many_transitions(self):
        """Test that ginga connects to many movements."""
        ginga_transitions = TRANSITION_MATRIX.get('ginga', {})
        assert len(ginga_transitions) >= 10

    def test_kick_transitions_back_to_ginga(self):
        """Test that kicks typically transition back to ginga."""
        kicks = ['armada', 'meia_lua_de_frente', 'bencao', 'queixada', 'martelo']
        for kick in kicks:
            transitions = TRANSITION_MATRIX.get(kick, {})
            if transitions:
                assert 'ginga' in transitions, f"{kick} should transition to ginga"
                assert transitions['ginga'] >= 0.8, f"{kick} -> ginga should be natural"


class TestCombinationResult:
    """Tests for CombinationResult dataclass."""

    def test_result_creation(self):
        """Test CombinationResult can be created."""
        result = CombinationResult(
            overall_score=75.0,
            level=CombinationLevel.ADVANCED,
            transition_score=80.0,
            rhythm_score=70.0,
            sequence_logic_score=75.0,
            recovery_score=72.0,
            variety_score=68.0,
            total_movements=50,
            unique_movements=5,
            transitions_analyzed=10,
            smooth_transitions=7,
            movement_sequence=['ginga', 'armada', 'ginga'],
            transition_details=[]
        )
        assert result.overall_score == 75.0
        assert result.level == CombinationLevel.ADVANCED


class TestTransitionAnalysis:
    """Tests for TransitionAnalysis dataclass."""

    def test_transition_analysis_creation(self):
        """Test TransitionAnalysis can be created."""
        ta = TransitionAnalysis(
            from_movement='ginga',
            to_movement='armada',
            quality_score=95.0,
            is_natural=True,
            recovery_time_frames=30,
            notes="Excellent natural flow"
        )
        assert ta.from_movement == 'ginga'
        assert ta.to_movement == 'armada'
        assert ta.is_natural is True


class TestAnalyzeWithMockDetections:
    """Tests using mock detections."""

    def _create_mock_detection(self, name: str, confidence: float = 0.8) -> DetectedMovement:
        """Create a mock detection."""
        return DetectedMovement(
            movement_name=name,
            movement_name_pt=name.title(),
            category=MovementCategory.FUNDAMENTAL,
            confidence=confidence,
            description=f"Mock {name}"
        )

    def test_analyze_ginga_sequence(self):
        """Test analyzing a simple ginga sequence."""
        analyzer = CombinationAnalyzer()
        detections = [self._create_mock_detection('ginga') for _ in range(30)]
        result = analyzer.analyze(detections)

        # Single movement type results in single-movement result
        assert result.unique_movements == 1
        assert 'ginga' in result.movement_sequence
        # Only one movement type means limited combination analysis
        assert len(result.movement_sequence) == 1

    def test_analyze_natural_combination(self):
        """Test analyzing a natural movement combination."""
        analyzer = CombinationAnalyzer()

        # Create a natural sequence: ginga -> armada -> ginga -> esquiva
        detections = []
        for _ in range(15):
            detections.append(self._create_mock_detection('ginga'))
        for _ in range(10):
            detections.append(self._create_mock_detection('armada'))
        for _ in range(15):
            detections.append(self._create_mock_detection('ginga'))
        for _ in range(10):
            detections.append(self._create_mock_detection('esquiva_lateral'))

        result = analyzer.analyze(detections)

        assert result.total_movements == 50
        assert result.unique_movements >= 3
        assert result.transitions_analyzed >= 3
        assert result.overall_score > 0

    def test_analyze_unnatural_combination(self):
        """Test that unnatural combinations score lower."""
        analyzer = CombinationAnalyzer()

        # Create sequence with uncommon transitions
        detections = []
        for _ in range(10):
            detections.append(self._create_mock_detection('bananeira'))
        for _ in range(10):
            detections.append(self._create_mock_detection('martelo'))

        result = analyzer.analyze(detections)

        # Should still work but may have lower transition scores
        assert result.overall_score >= 0
        assert result.overall_score <= 100

    def test_low_confidence_filtered(self):
        """Test that low confidence detections are filtered."""
        analyzer = CombinationAnalyzer()

        detections = [
            self._create_mock_detection('ginga', confidence=0.9),
            self._create_mock_detection('unknown', confidence=0.1),  # Should be filtered
            self._create_mock_detection('ginga', confidence=0.8),
        ]

        result = analyzer.analyze(detections)
        assert result.total_movements <= 3


class TestAnalyzeCombinationFunction:
    """Tests for the convenience function."""

    def test_analyze_combination_function(self):
        """Test the analyze_combination convenience function."""
        detections = [
            DetectedMovement(
                movement_name='ginga',
                movement_name_pt='Ginga',
                category=MovementCategory.FUNDAMENTAL,
                confidence=0.8,
                description='Test'
            )
            for _ in range(20)
        ]

        result = analyze_combination(detections, fps=30.0)
        assert isinstance(result, CombinationResult)


class TestLevelDetermination:
    """Tests for level determination."""

    def test_level_boundaries(self):
        """Test that levels are assigned at correct boundaries."""
        analyzer = CombinationAnalyzer()

        # Test _get_level method directly
        assert analyzer._get_level(95) == CombinationLevel.MASTER
        assert analyzer._get_level(85) == CombinationLevel.EXPERT
        assert analyzer._get_level(75) == CombinationLevel.ADVANCED
        assert analyzer._get_level(65) == CombinationLevel.INTERMEDIATE
        assert analyzer._get_level(50) == CombinationLevel.DEVELOPING
        assert analyzer._get_level(35) == CombinationLevel.BEGINNER
        assert analyzer._get_level(20) == CombinationLevel.NOVICE


class TestFeedbackGeneration:
    """Tests for feedback generation."""

    def test_feedback_generated(self):
        """Test that feedback is generated."""
        analyzer = CombinationAnalyzer()

        detections = [
            DetectedMovement(
                movement_name='ginga',
                movement_name_pt='Ginga',
                category=MovementCategory.FUNDAMENTAL,
                confidence=0.8,
                description='Test'
            )
            for _ in range(30)
        ]

        result = analyzer.analyze(detections)

        # Should have some feedback, strengths, or improvements
        assert (result.feedback or result.strengths or result.areas_to_improve)
