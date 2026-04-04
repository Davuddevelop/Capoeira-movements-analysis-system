"""
Automatic Movement Detection System

This module automatically detects which capoeira movement is being performed
based on body pose analysis. It uses landmark positions and joint angles
to classify movements in real-time.

DETECTION APPROACH:
1. Analyze body position (standing, ground, inverted)
2. Check limb configurations (which limbs are raised/extended)
3. Match against movement signatures
4. Return detected movement with confidence score

SUPPORTED MOVEMENTS (20+):
- Fundamental: Ginga
- Kicks: Armada, Meia-lua, Bencao, Queixada, Martelo, Ponteira, Chapa, Gancho
- Defenses: Esquiva, Cocorinha, Negativa, Role
- Acrobatics: Au, Bananeira, Ponte, Queda de Rins, Macaco
- Ground: Negativa, Role, Rasteira

Sources:
- DendeArts fundamental movements guide
- LaLaue complete movements list (200+ techniques)
- CapoeiraWiki movement descriptions
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class MovementCategory(Enum):
    """Categories of capoeira movements."""
    FUNDAMENTAL = "fundamental"
    KICK = "kick"
    DEFENSE = "defense"
    ACROBATIC = "acrobatic"
    GROUND = "ground"
    TAKEDOWN = "takedown"
    UNKNOWN = "unknown"


@dataclass
class DetectedMovement:
    """Result of movement detection."""
    movement_name: str
    movement_name_pt: str
    category: MovementCategory
    confidence: float  # 0.0 to 1.0
    description: str
    secondary_guess: Optional[str] = None
    secondary_confidence: float = 0.0


@dataclass
class BodyState:
    """Analyzed state of the body from landmarks."""
    # Vertical position
    is_standing: bool = True
    is_crouching: bool = False
    is_on_ground: bool = False
    is_inverted: bool = False

    # Limb states
    left_leg_raised: bool = False
    right_leg_raised: bool = False
    left_leg_extended: bool = False
    right_leg_extended: bool = False
    left_arm_on_ground: bool = False
    right_arm_on_ground: bool = False

    # Body orientation
    facing_direction: str = "forward"  # forward, left, right, back
    spine_angle: float = 180.0

    # Heights (relative to hip)
    left_foot_height: float = 0.0
    right_foot_height: float = 0.0
    head_height: float = 1.0
    hip_height: float = 0.5


class MovementDetector:
    """
    Detects capoeira movements from pose landmarks.

    Uses a rule-based system combined with angle analysis to identify
    which movement is being performed.
    """

    # Landmark indices (MediaPipe)
    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT = 31
    RIGHT_FOOT = 32

    def __init__(self, min_confidence: float = 0.3):
        """
        Initialize the movement detector.

        Args:
            min_confidence: Minimum confidence to report a detection
        """
        self.min_confidence = min_confidence
        self._init_movement_signatures()

    def _init_movement_signatures(self):
        """Initialize movement signature definitions."""
        self.movements = {
            # ===== FUNDAMENTAL =====
            'ginga': {
                'name_pt': 'Ginga',
                'category': MovementCategory.FUNDAMENTAL,
                'description': 'Basic swaying movement with alternating lunges',
                'signatures': ['standing', 'one_knee_bent', 'arms_guard'],
            },

            # ===== KICKS =====
            'armada': {
                'name_pt': 'Armada',
                'category': MovementCategory.KICK,
                'description': '360° spinning kick with outside of foot',
                'signatures': ['standing', 'one_leg_high', 'spinning'],
            },
            'meia_lua_de_frente': {
                'name_pt': 'Meia-lua de Frente',
                'category': MovementCategory.KICK,
                'description': 'Outside crescent kick across face',
                'signatures': ['standing', 'one_leg_high_side', 'leg_extended'],
            },
            'bencao': {
                'name_pt': 'Bênção',
                'category': MovementCategory.KICK,
                'description': 'Front push kick to chest/stomach',
                'signatures': ['standing', 'one_leg_forward', 'leg_extended'],
            },
            'queixada': {
                'name_pt': 'Queixada',
                'category': MovementCategory.KICK,
                'description': 'Inside-out crescent kick',
                'signatures': ['standing', 'one_leg_high_side', 'body_rotating'],
            },
            'martelo': {
                'name_pt': 'Martelo',
                'category': MovementCategory.KICK,
                'description': 'Roundhouse kick with instep',
                'signatures': ['standing', 'one_leg_high_side', 'hip_rotated'],
            },
            'ponteira': {
                'name_pt': 'Ponteira',
                'category': MovementCategory.KICK,
                'description': 'Front snap kick with ball of foot',
                'signatures': ['standing', 'one_leg_forward', 'quick_motion'],
            },
            'chapa': {
                'name_pt': 'Chapa',
                'category': MovementCategory.KICK,
                'description': 'Side push kick',
                'signatures': ['standing', 'one_leg_side', 'leg_extended'],
            },
            'gancho': {
                'name_pt': 'Gancho',
                'category': MovementCategory.KICK,
                'description': 'Hook kick striking with heel',
                'signatures': ['standing', 'one_leg_high', 'leg_bent_hook'],
            },
            'meia_lua_de_compasso': {
                'name_pt': 'Meia-lua de Compasso',
                'category': MovementCategory.KICK,
                'description': 'Spinning kick with hand on ground',
                'signatures': ['one_hand_ground', 'one_leg_high', 'spinning'],
            },

            # ===== DEFENSES =====
            'esquiva_lateral': {
                'name_pt': 'Esquiva Lateral',
                'category': MovementCategory.DEFENSE,
                'description': 'Side dodge from ginga',
                'signatures': ['crouching', 'both_feet_ground', 'leaning_side'],
            },
            'esquiva_baixa': {
                'name_pt': 'Esquiva Baixa',
                'category': MovementCategory.DEFENSE,
                'description': 'Deep low dodge',
                'signatures': ['very_low', 'both_feet_ground', 'one_hand_guard'],
            },
            'cocorinha': {
                'name_pt': 'Cocorinha',
                'category': MovementCategory.DEFENSE,
                'description': 'Squat dodge with hand protecting face',
                'signatures': ['squatting', 'both_feet_ground', 'compact'],
            },
            'negativa': {
                'name_pt': 'Negativa',
                'category': MovementCategory.DEFENSE,
                'description': 'Ground evasion with one leg extended',
                'signatures': ['on_ground', 'one_leg_extended', 'hand_support'],
            },
            'role': {
                'name_pt': 'Rolê',
                'category': MovementCategory.DEFENSE,
                'description': 'Low spinning movement on ground',
                'signatures': ['on_ground', 'hands_ground', 'spinning_low'],
            },

            # ===== ACROBATICS =====
            'au': {
                'name_pt': 'Aú',
                'category': MovementCategory.ACROBATIC,
                'description': 'Capoeira cartwheel',
                'signatures': ['inverted', 'hands_ground', 'legs_spread'],
            },
            'au_batido': {
                'name_pt': 'Aú Batido',
                'category': MovementCategory.ACROBATIC,
                'description': 'Cartwheel with kick',
                'signatures': ['inverted', 'hands_ground', 'one_leg_kicking'],
            },
            'bananeira': {
                'name_pt': 'Bananeira',
                'category': MovementCategory.ACROBATIC,
                'description': 'Handstand position',
                'signatures': ['inverted', 'hands_ground', 'legs_up'],
            },
            'macaco': {
                'name_pt': 'Macaco',
                'category': MovementCategory.ACROBATIC,
                'description': 'Back handspring from low position',
                'signatures': ['transitioning', 'hand_back', 'flipping'],
            },
            'ponte': {
                'name_pt': 'Ponte',
                'category': MovementCategory.ACROBATIC,
                'description': 'Back bridge position',
                'signatures': ['bridge', 'hands_ground', 'feet_ground', 'arched'],
            },
            'queda_de_rins': {
                'name_pt': 'Queda de Rins',
                'category': MovementCategory.ACROBATIC,
                'description': 'Elbow balance with twisted hips',
                'signatures': ['inverted', 'elbow_support', 'hips_twisted'],
            },

            # ===== TAKEDOWNS =====
            'rasteira': {
                'name_pt': 'Rasteira',
                'category': MovementCategory.TAKEDOWN,
                'description': 'Leg sweep from ground',
                'signatures': ['low', 'one_leg_sweeping', 'hands_support'],
            },
            'banda': {
                'name_pt': 'Banda',
                'category': MovementCategory.TAKEDOWN,
                'description': 'Standing leg sweep',
                'signatures': ['standing', 'one_leg_sweeping_low'],
            },
            'tesoura': {
                'name_pt': 'Tesoura',
                'category': MovementCategory.TAKEDOWN,
                'description': 'Scissors takedown',
                'signatures': ['on_ground', 'legs_crossing', 'opponent_trapped'],
            },
        }

    def _extract_body_state(self, landmarks) -> BodyState:
        """
        Extract body state from MediaPipe landmarks.

        Args:
            landmarks: MediaPipe pose landmarks

        Returns:
            BodyState with analyzed body position
        """
        state = BodyState()

        if landmarks is None:
            return state

        try:
            # Get key landmark positions
            nose = landmarks[self.NOSE]
            left_hip = landmarks[self.LEFT_HIP]
            right_hip = landmarks[self.RIGHT_HIP]
            left_knee = landmarks[self.LEFT_KNEE]
            right_knee = landmarks[self.RIGHT_KNEE]
            left_ankle = landmarks[self.LEFT_ANKLE]
            right_ankle = landmarks[self.RIGHT_ANKLE]
            left_wrist = landmarks[self.LEFT_WRIST]
            right_wrist = landmarks[self.RIGHT_WRIST]
            left_shoulder = landmarks[self.LEFT_SHOULDER]
            right_shoulder = landmarks[self.RIGHT_SHOULDER]

            # Calculate hip center
            hip_y = (left_hip.y + right_hip.y) / 2
            shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

            # Height analysis (y increases downward in image coordinates)
            state.left_foot_height = hip_y - left_ankle.y
            state.right_foot_height = hip_y - right_ankle.y
            state.head_height = hip_y - nose.y
            state.hip_height = 1 - hip_y  # Relative to image bottom

            # Is inverted? (head below hips)
            state.is_inverted = nose.y > hip_y

            # Is on ground? (hips very low)
            state.is_on_ground = hip_y > 0.7

            # Is crouching? (hips medium-low)
            state.is_crouching = 0.5 < hip_y < 0.7 and not state.is_inverted

            # Is standing? (hips medium-high)
            state.is_standing = hip_y <= 0.5 and not state.is_inverted

            # Leg raised detection (foot significantly higher than other foot)
            height_diff = abs(state.left_foot_height - state.right_foot_height)
            if height_diff > 0.15:  # Significant height difference
                if state.left_foot_height > state.right_foot_height:
                    state.left_leg_raised = True
                else:
                    state.right_leg_raised = True

            # Leg extended (knee angle > 150)
            # Calculate knee angles
            def calc_angle(a, b, c):
                ba = np.array([a.x - b.x, a.y - b.y])
                bc = np.array([c.x - b.x, c.y - b.y])
                cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
                return np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))

            left_knee_angle = calc_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = calc_angle(right_hip, right_knee, right_ankle)

            state.left_leg_extended = left_knee_angle > 150
            state.right_leg_extended = right_knee_angle > 150

            # Arms on ground (wrist below hip level)
            state.left_arm_on_ground = left_wrist.y > hip_y + 0.1
            state.right_arm_on_ground = right_wrist.y > hip_y + 0.1

            # Spine angle (simplified - using shoulder-hip alignment)
            spine_vector = np.array([
                (left_shoulder.x + right_shoulder.x) / 2 - (left_hip.x + right_hip.x) / 2,
                (left_shoulder.y + right_shoulder.y) / 2 - (left_hip.y + right_hip.y) / 2
            ])
            vertical = np.array([0, -1])  # Up in image coordinates
            cos_spine = np.dot(spine_vector, vertical) / (np.linalg.norm(spine_vector) + 1e-6)
            state.spine_angle = np.degrees(np.arccos(np.clip(cos_spine, -1, 1)))

        except (IndexError, AttributeError):
            pass

        return state

    def detect(self, landmarks, angles: Dict[str, Optional[float]] = None) -> DetectedMovement:
        """
        Detect which movement is being performed.

        Args:
            landmarks: MediaPipe pose landmarks (list or landmark object)
            angles: Optional pre-calculated joint angles

        Returns:
            DetectedMovement with movement identification
        """
        if landmarks is None:
            return DetectedMovement(
                movement_name="unknown",
                movement_name_pt="Desconhecido",
                category=MovementCategory.UNKNOWN,
                confidence=0.0,
                description="No pose detected"
            )

        # Convert landmarks if needed
        if hasattr(landmarks, 'landmark'):
            landmarks = landmarks.landmark

        # Extract body state
        state = self._extract_body_state(landmarks)

        # Score each movement
        scores = {}

        # ===== INVERTED MOVEMENTS =====
        if state.is_inverted:
            if state.left_arm_on_ground and state.right_arm_on_ground:
                if state.left_leg_extended and state.right_leg_extended:
                    scores['bananeira'] = 0.85
                    scores['au'] = 0.75
                else:
                    scores['au'] = 0.80
                    scores['queda_de_rins'] = 0.60
            elif state.left_arm_on_ground or state.right_arm_on_ground:
                scores['au'] = 0.70
                scores['macaco'] = 0.50

        # ===== BRIDGE POSITION =====
        elif state.spine_angle > 120 and (state.left_arm_on_ground or state.right_arm_on_ground):
            scores['ponte'] = 0.80

        # ===== GROUND MOVEMENTS =====
        elif state.is_on_ground:
            if state.left_leg_extended or state.right_leg_extended:
                scores['negativa'] = 0.85
                scores['rasteira'] = 0.60
            elif state.left_arm_on_ground or state.right_arm_on_ground:
                scores['role'] = 0.75
                scores['tesoura'] = 0.50
            else:
                scores['negativa'] = 0.60

        # ===== CROUCHING MOVEMENTS =====
        elif state.is_crouching:
            if state.spine_angle < 160:  # Leaning
                scores['esquiva_lateral'] = 0.85
                scores['esquiva_baixa'] = 0.70
            else:
                scores['cocorinha'] = 0.80
                scores['esquiva_baixa'] = 0.65

        # ===== STANDING WITH LEG RAISED (KICKS) =====
        elif state.is_standing and (state.left_leg_raised or state.right_leg_raised):
            raised_extended = (state.left_leg_raised and state.left_leg_extended) or \
                             (state.right_leg_raised and state.right_leg_extended)

            if raised_extended:
                # Determine kick type based on leg position and angles
                if angles:
                    hip_angle = angles.get('left_hip') if state.left_leg_raised else angles.get('right_hip')
                    if hip_angle:
                        if hip_angle < 100:  # High kick
                            scores['martelo'] = 0.75
                            scores['meia_lua_de_frente'] = 0.70
                            scores['armada'] = 0.65
                        else:
                            scores['bencao'] = 0.80
                            scores['chapa'] = 0.65
                else:
                    scores['martelo'] = 0.70
                    scores['bencao'] = 0.65
                    scores['meia_lua_de_frente'] = 0.60
            else:
                # Leg raised but bent - could be chambering
                scores['ponteira'] = 0.60
                scores['gancho'] = 0.55
                scores['bencao'] = 0.50

            # Check for hand on ground (meia lua de compasso)
            if state.left_arm_on_ground or state.right_arm_on_ground:
                scores['meia_lua_de_compasso'] = 0.85

        # ===== STANDING NORMAL (GINGA or transition) =====
        elif state.is_standing:
            scores['ginga'] = 0.80
            scores['banda'] = 0.30

        # ===== UNKNOWN =====
        else:
            scores['ginga'] = 0.40  # Default fallback

        # Find best match
        if not scores:
            return DetectedMovement(
                movement_name="unknown",
                movement_name_pt="Desconhecido",
                category=MovementCategory.UNKNOWN,
                confidence=0.0,
                description="Unable to classify movement"
            )

        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_match = sorted_scores[0]
        second_match = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)

        movement_info = self.movements.get(best_match[0], {})

        result = DetectedMovement(
            movement_name=best_match[0],
            movement_name_pt=movement_info.get('name_pt', best_match[0]),
            category=movement_info.get('category', MovementCategory.UNKNOWN),
            confidence=best_match[1],
            description=movement_info.get('description', ''),
            secondary_guess=second_match[0] if second_match[1] > self.min_confidence else None,
            secondary_confidence=second_match[1]
        )

        return result

    def detect_sequence(self, landmarks_sequence: List,
                       angles_sequence: List[Dict] = None) -> List[DetectedMovement]:
        """
        Detect movements across a sequence of frames.

        Args:
            landmarks_sequence: List of landmarks for each frame
            angles_sequence: Optional list of angle dictionaries

        Returns:
            List of DetectedMovement for each frame
        """
        results = []
        for i, landmarks in enumerate(landmarks_sequence):
            angles = angles_sequence[i] if angles_sequence else None
            results.append(self.detect(landmarks, angles))
        return results

    def get_dominant_movement(self, detections: List[DetectedMovement]) -> DetectedMovement:
        """
        Get the most commonly detected movement from a sequence.

        Args:
            detections: List of frame-by-frame detections

        Returns:
            Most frequently detected movement
        """
        if not detections:
            return DetectedMovement(
                movement_name="unknown",
                movement_name_pt="Desconhecido",
                category=MovementCategory.UNKNOWN,
                confidence=0.0,
                description="No detections"
            )

        # Count occurrences weighted by confidence
        movement_scores = {}
        for det in detections:
            if det.confidence >= self.min_confidence:
                name = det.movement_name
                if name not in movement_scores:
                    movement_scores[name] = {'count': 0, 'total_conf': 0, 'detection': det}
                movement_scores[name]['count'] += 1
                movement_scores[name]['total_conf'] += det.confidence

        if not movement_scores:
            return detections[0]

        # Find best by count * average confidence
        best_name = max(movement_scores.keys(),
                       key=lambda x: movement_scores[x]['count'] *
                                    (movement_scores[x]['total_conf'] / movement_scores[x]['count']))

        best = movement_scores[best_name]
        result = best['detection']
        result.confidence = best['total_conf'] / best['count']

        return result

    def get_all_movements(self) -> Dict[str, Dict]:
        """Return all supported movements with their info."""
        return self.movements.copy()

    def get_movements_by_category(self, category: MovementCategory) -> List[str]:
        """Get all movements in a specific category."""
        return [name for name, info in self.movements.items()
                if info['category'] == category]


def create_detector() -> MovementDetector:
    """Create and return a MovementDetector instance."""
    return MovementDetector()
