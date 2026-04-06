"""
Tests for the automatic movement detection system.
"""

import pytest
from unittest.mock import MagicMock
from analyzer.movement_detector import (
    MovementDetector,
    MovementCategory,
    DetectedMovement,
    BodyState,
    create_detector
)


class TestMovementDetector:
    """Tests for MovementDetector class."""

    def test_detector_creation(self):
        """Test that detector can be created."""
        detector = MovementDetector()
        assert detector is not None
        assert detector.min_confidence == 0.3

    def test_detector_with_custom_confidence(self):
        """Test detector with custom confidence threshold."""
        detector = MovementDetector(min_confidence=0.5)
        assert detector.min_confidence == 0.5

    def test_detector_has_movements(self):
        """Test that detector has movement definitions."""
        detector = MovementDetector()
        assert len(detector.movements) >= 20  # At least 20 movements

    def test_all_movements_have_required_fields(self):
        """Test that all movement definitions have required fields."""
        detector = MovementDetector()
        for name, info in detector.movements.items():
            assert 'name_pt' in info, f"{name} missing name_pt"
            assert 'category' in info, f"{name} missing category"
            assert 'description' in info, f"{name} missing description"
            assert 'signatures' in info, f"{name} missing signatures"

    def test_detect_returns_detected_movement(self):
        """Test that detect returns a DetectedMovement object."""
        detector = MovementDetector()
        # Test with None landmarks
        result = detector.detect(None)
        assert isinstance(result, DetectedMovement)
        assert result.movement_name == "unknown"
        assert result.confidence == 0.0


class TestMovementCategory:
    """Tests for MovementCategory enum."""

    def test_all_categories_exist(self):
        """Test that all expected categories exist."""
        assert MovementCategory.FUNDAMENTAL.value == "fundamental"
        assert MovementCategory.KICK.value == "kick"
        assert MovementCategory.DEFENSE.value == "defense"
        assert MovementCategory.ACROBATIC.value == "acrobatic"
        assert MovementCategory.GROUND.value == "ground"
        assert MovementCategory.TAKEDOWN.value == "takedown"
        assert MovementCategory.UNKNOWN.value == "unknown"


class TestDetectedMovement:
    """Tests for DetectedMovement dataclass."""

    def test_detected_movement_creation(self):
        """Test DetectedMovement can be created."""
        dm = DetectedMovement(
            movement_name="ginga",
            movement_name_pt="Ginga",
            category=MovementCategory.FUNDAMENTAL,
            confidence=0.85,
            description="Basic swaying movement"
        )
        assert dm.movement_name == "ginga"
        assert dm.movement_name_pt == "Ginga"
        assert dm.category == MovementCategory.FUNDAMENTAL
        assert dm.confidence == 0.85
        assert dm.secondary_guess is None
        assert dm.secondary_confidence == 0.0

    def test_detected_movement_with_secondary(self):
        """Test DetectedMovement with secondary guess."""
        dm = DetectedMovement(
            movement_name="martelo",
            movement_name_pt="Martelo",
            category=MovementCategory.KICK,
            confidence=0.70,
            description="Roundhouse kick",
            secondary_guess="armada",
            secondary_confidence=0.60
        )
        assert dm.secondary_guess == "armada"
        assert dm.secondary_confidence == 0.60


class TestBodyState:
    """Tests for BodyState dataclass."""

    def test_body_state_defaults(self):
        """Test BodyState default values."""
        state = BodyState()
        assert state.is_standing is True
        assert state.is_crouching is False
        assert state.is_on_ground is False
        assert state.is_inverted is False
        assert state.left_leg_raised is False
        assert state.right_leg_raised is False
        assert state.facing_direction == "forward"
        assert state.spine_angle == 180.0


class TestMovementsByCategory:
    """Tests for getting movements by category."""

    def test_get_kicks(self):
        """Test getting kick movements."""
        detector = MovementDetector()
        kicks = detector.get_movements_by_category(MovementCategory.KICK)
        assert len(kicks) >= 5  # At least 5 kicks
        assert 'martelo' in kicks
        assert 'bencao' in kicks
        assert 'armada' in kicks

    def test_get_defenses(self):
        """Test getting defense movements."""
        detector = MovementDetector()
        defenses = detector.get_movements_by_category(MovementCategory.DEFENSE)
        assert len(defenses) >= 3  # At least 3 defenses
        assert 'negativa' in defenses

    def test_get_acrobatics(self):
        """Test getting acrobatic movements."""
        detector = MovementDetector()
        acrobatics = detector.get_movements_by_category(MovementCategory.ACROBATIC)
        assert len(acrobatics) >= 4  # At least 4 acrobatics
        assert 'au' in acrobatics
        assert 'bananeira' in acrobatics


class TestCreateDetector:
    """Tests for create_detector factory function."""

    def test_create_detector_function(self):
        """Test that create_detector returns a MovementDetector."""
        detector = create_detector()
        assert isinstance(detector, MovementDetector)


class TestGetAllMovements:
    """Tests for get_all_movements method."""

    def test_get_all_movements(self):
        """Test getting all movements."""
        detector = MovementDetector()
        all_movements = detector.get_all_movements()
        assert isinstance(all_movements, dict)
        assert len(all_movements) >= 20

    def test_get_all_movements_returns_copy(self):
        """Test that get_all_movements returns a copy."""
        detector = MovementDetector()
        movements1 = detector.get_all_movements()
        movements2 = detector.get_all_movements()
        assert movements1 is not movements2


class TestMockLandmarkDetection:
    """Tests using mock landmarks."""

    def _create_mock_landmark(self, x, y, z=0.0, visibility=1.0):
        """Create a mock landmark object."""
        landmark = MagicMock()
        landmark.x = x
        landmark.y = y
        landmark.z = z
        landmark.visibility = visibility
        return landmark

    def _create_standing_landmarks(self):
        """Create landmarks for a standing pose."""
        # Create 33 landmarks (MediaPipe format)
        landmarks = []
        for i in range(33):
            landmarks.append(self._create_mock_landmark(0.5, 0.5))

        # Set specific positions for standing
        # Nose at top
        landmarks[0] = self._create_mock_landmark(0.5, 0.2)
        # Shoulders
        landmarks[11] = self._create_mock_landmark(0.4, 0.3)
        landmarks[12] = self._create_mock_landmark(0.6, 0.3)
        # Hips
        landmarks[23] = self._create_mock_landmark(0.4, 0.5)
        landmarks[24] = self._create_mock_landmark(0.6, 0.5)
        # Knees
        landmarks[25] = self._create_mock_landmark(0.4, 0.65)
        landmarks[26] = self._create_mock_landmark(0.6, 0.65)
        # Ankles
        landmarks[27] = self._create_mock_landmark(0.4, 0.8)
        landmarks[28] = self._create_mock_landmark(0.6, 0.8)
        # Wrists (hands up in guard)
        landmarks[15] = self._create_mock_landmark(0.35, 0.35)
        landmarks[16] = self._create_mock_landmark(0.65, 0.35)

        return landmarks

    def _create_inverted_landmarks(self):
        """Create landmarks for an inverted pose (handstand/au)."""
        landmarks = []
        for i in range(33):
            landmarks.append(self._create_mock_landmark(0.5, 0.5))

        # Head below hips for inverted
        landmarks[0] = self._create_mock_landmark(0.5, 0.8)  # Nose low
        # Shoulders low
        landmarks[11] = self._create_mock_landmark(0.4, 0.7)
        landmarks[12] = self._create_mock_landmark(0.6, 0.7)
        # Hips high
        landmarks[23] = self._create_mock_landmark(0.4, 0.4)
        landmarks[24] = self._create_mock_landmark(0.6, 0.4)
        # Knees high
        landmarks[25] = self._create_mock_landmark(0.4, 0.25)
        landmarks[26] = self._create_mock_landmark(0.6, 0.25)
        # Ankles at top
        landmarks[27] = self._create_mock_landmark(0.4, 0.1)
        landmarks[28] = self._create_mock_landmark(0.6, 0.1)
        # Wrists on ground
        landmarks[15] = self._create_mock_landmark(0.35, 0.85)
        landmarks[16] = self._create_mock_landmark(0.65, 0.85)

        return landmarks

    def test_detect_standing_pose(self):
        """Test detecting a standing pose (should detect ginga)."""
        detector = MovementDetector()
        landmarks = self._create_standing_landmarks()
        result = detector.detect(landmarks)

        assert result.confidence > 0
        # Standing pose should be classified as ginga or similar
        assert result.movement_name in ['ginga', 'banda', 'unknown']

    def test_detect_inverted_pose(self):
        """Test detecting an inverted pose (should detect au/bananeira)."""
        detector = MovementDetector()
        landmarks = self._create_inverted_landmarks()
        result = detector.detect(landmarks)

        assert result.confidence > 0
        # Inverted pose should be classified as au or bananeira
        assert result.movement_name in ['au', 'bananeira', 'macaco', 'queda_de_rins']


class TestSequenceDetection:
    """Tests for sequence detection."""

    def test_detect_sequence_empty(self):
        """Test detecting movements in empty sequence."""
        detector = MovementDetector()
        result = detector.detect_sequence([])
        assert result == []

    def test_get_dominant_movement_empty(self):
        """Test getting dominant movement from empty list."""
        detector = MovementDetector()
        result = detector.get_dominant_movement([])
        assert result.movement_name == "unknown"
        assert result.confidence == 0.0

    def test_get_dominant_movement_single(self):
        """Test getting dominant movement from single detection."""
        detector = MovementDetector()
        detection = DetectedMovement(
            movement_name="ginga",
            movement_name_pt="Ginga",
            category=MovementCategory.FUNDAMENTAL,
            confidence=0.8,
            description="Test"
        )
        result = detector.get_dominant_movement([detection])
        assert result.movement_name == "ginga"
