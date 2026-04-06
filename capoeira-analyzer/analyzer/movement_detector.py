"""
Automatic Movement Detection System - REWRITTEN FOR ACCURACY

This module automatically detects which capoeira movement is being performed
based on body pose analysis. It uses landmark positions and joint angles
to classify movements in real-time.

CORE 10 MOVEMENTS (must detect reliably):
1. Ginga - Base swaying movement
2. Au - Cartwheel (both hands on ground, inverted)
3. Meia Lua de Compasso - One hand ground, leg sweep
4. Armada - Spinning high kick
5. Martelo - Roundhouse kick
6. Bencao - Front push kick
7. Queixada - Inside crescent kick
8. Esquiva - Dodge/crouch
9. Negativa - Ground position with extended leg
10. Role - Low spinning movement

Detection Strategy:
- Use MULTIPLE indicators for each movement
- Very LOW thresholds to catch movements
- Check specific movements FIRST, ginga LAST
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
    # Raw landmark data
    nose_y: float = 0.5
    hip_y: float = 0.5
    left_ankle_y: float = 0.8
    right_ankle_y: float = 0.8
    left_wrist_y: float = 0.5
    right_wrist_y: float = 0.5
    left_knee_y: float = 0.6
    right_knee_y: float = 0.6

    # Computed states
    head_below_hips: bool = False
    left_hand_low: bool = False
    right_hand_low: bool = False
    left_leg_high: bool = False
    right_leg_high: bool = False
    body_low: bool = False
    body_very_low: bool = False

    # Angles
    left_knee_angle: float = 180.0
    right_knee_angle: float = 180.0
    spine_angle: float = 180.0


class MovementDetector:
    """
    Detects capoeira movements from pose landmarks.

    REWRITTEN for much better accuracy on core movements.
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

    # Movement definitions
    MOVEMENTS = {
        'ginga': {
            'name_pt': 'Ginga',
            'category': MovementCategory.FUNDAMENTAL,
            'description': 'Basic swaying movement - the foundation of capoeira',
        },
        'au': {
            'name_pt': 'Aú',
            'category': MovementCategory.ACROBATIC,
            'description': 'Cartwheel - inverted with both hands on ground',
        },
        'meia_lua_de_compasso': {
            'name_pt': 'Meia-lua de Compasso',
            'category': MovementCategory.KICK,
            'description': 'Compass half-moon kick - hand on ground, sweeping leg',
        },
        'armada': {
            'name_pt': 'Armada',
            'category': MovementCategory.KICK,
            'description': 'Spinning outside kick - high and powerful',
        },
        'martelo': {
            'name_pt': 'Martelo',
            'category': MovementCategory.KICK,
            'description': 'Hammer kick - roundhouse style',
        },
        'bencao': {
            'name_pt': 'Bênção',
            'category': MovementCategory.KICK,
            'description': 'Blessing kick - front push kick',
        },
        'queixada': {
            'name_pt': 'Queixada',
            'category': MovementCategory.KICK,
            'description': 'Jaw kick - outside to inside crescent',
        },
        'meia_lua_de_frente': {
            'name_pt': 'Meia-lua de Frente',
            'category': MovementCategory.KICK,
            'description': 'Front half-moon kick',
        },
        'chapa': {
            'name_pt': 'Chapa',
            'category': MovementCategory.KICK,
            'description': 'Side stomp kick',
        },
        'ponteira': {
            'name_pt': 'Ponteira',
            'category': MovementCategory.KICK,
            'description': 'Front snap kick',
        },
        'gancho': {
            'name_pt': 'Gancho',
            'category': MovementCategory.KICK,
            'description': 'Hook kick',
        },
        'esquiva_lateral': {
            'name_pt': 'Esquiva Lateral',
            'category': MovementCategory.DEFENSE,
            'description': 'Side dodge from attack',
        },
        'esquiva_baixa': {
            'name_pt': 'Esquiva Baixa',
            'category': MovementCategory.DEFENSE,
            'description': 'Low dodge',
        },
        'cocorinha': {
            'name_pt': 'Cocorinha',
            'category': MovementCategory.DEFENSE,
            'description': 'Squat dodge with hand guard',
        },
        'negativa': {
            'name_pt': 'Negativa',
            'category': MovementCategory.GROUND,
            'description': 'Ground position with extended leg',
        },
        'role': {
            'name_pt': 'Rolê',
            'category': MovementCategory.GROUND,
            'description': 'Low spinning escape movement',
        },
        'bananeira': {
            'name_pt': 'Bananeira',
            'category': MovementCategory.ACROBATIC,
            'description': 'Handstand position',
        },
        'macaco': {
            'name_pt': 'Macaco',
            'category': MovementCategory.ACROBATIC,
            'description': 'Back handspring from crouch',
        },
        'rabo_de_arraia': {
            'name_pt': 'Rabo de Arraia',
            'category': MovementCategory.KICK,
            'description': 'Stingray tail - spinning low kick',
        },
        'rasteira': {
            'name_pt': 'Rasteira',
            'category': MovementCategory.TAKEDOWN,
            'description': 'Leg sweep takedown',
        },
    }

    def __init__(self, min_confidence: float = 0.2):
        self.min_confidence = min_confidence

    def _get_landmark_values(self, landmarks) -> dict:
        """Extract raw y-values from landmarks."""
        if landmarks is None:
            return None

        try:
            return {
                'nose_y': landmarks[self.NOSE].y,
                'left_shoulder_y': landmarks[self.LEFT_SHOULDER].y,
                'right_shoulder_y': landmarks[self.RIGHT_SHOULDER].y,
                'left_hip_y': landmarks[self.LEFT_HIP].y,
                'right_hip_y': landmarks[self.RIGHT_HIP].y,
                'left_knee_y': landmarks[self.LEFT_KNEE].y,
                'right_knee_y': landmarks[self.RIGHT_KNEE].y,
                'left_ankle_y': landmarks[self.LEFT_ANKLE].y,
                'right_ankle_y': landmarks[self.RIGHT_ANKLE].y,
                'left_wrist_y': landmarks[self.LEFT_WRIST].y,
                'right_wrist_y': landmarks[self.RIGHT_WRIST].y,
                'left_wrist_x': landmarks[self.LEFT_WRIST].x,
                'right_wrist_x': landmarks[self.RIGHT_WRIST].x,
                'left_ankle_x': landmarks[self.LEFT_ANKLE].x,
                'right_ankle_x': landmarks[self.RIGHT_ANKLE].x,
            }
        except (IndexError, AttributeError):
            return None

    def _calc_angle(self, landmarks, idx1, idx2, idx3) -> float:
        """Calculate angle between three landmarks."""
        try:
            a = landmarks[idx1]
            b = landmarks[idx2]
            c = landmarks[idx3]

            ba = np.array([a.x - b.x, a.y - b.y])
            bc = np.array([c.x - b.x, c.y - b.y])

            cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
            return np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
        except:
            return 180.0

    def detect(self, landmarks, angles: Dict[str, Optional[float]] = None) -> DetectedMovement:
        """
        Detect which movement is being performed.

        Uses a scoring system that checks SPECIFIC movements first.
        Ginga is only detected if nothing else matches.
        """
        if landmarks is None:
            return self._unknown("No pose detected")

        # Convert landmarks if needed
        if hasattr(landmarks, 'landmark'):
            landmarks = landmarks.landmark

        # Get raw values
        vals = self._get_landmark_values(landmarks)
        if vals is None:
            return self._unknown("Failed to extract landmarks")

        # Calculate key measurements
        hip_y = (vals['left_hip_y'] + vals['right_hip_y']) / 2
        shoulder_y = (vals['left_shoulder_y'] + vals['right_shoulder_y']) / 2
        nose_y = vals['nose_y']

        left_ankle_y = vals['left_ankle_y']
        right_ankle_y = vals['right_ankle_y']
        left_wrist_y = vals['left_wrist_y']
        right_wrist_y = vals['right_wrist_y']
        left_knee_y = vals['left_knee_y']
        right_knee_y = vals['right_knee_y']

        # Calculate angles
        left_knee_angle = self._calc_angle(landmarks, self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE)
        right_knee_angle = self._calc_angle(landmarks, self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE)

        # =================================================================
        # KEY INDICATORS (using normalized 0-1 coordinates where 0=top, 1=bottom)
        # Higher y value = lower in frame (closer to ground)
        # =================================================================

        # Head position relative to hips
        head_below_hips = nose_y > hip_y + 0.03  # More sensitive
        head_way_below_hips = nose_y > hip_y + 0.10

        # Hand positions - RELAXED thresholds to catch more movements
        # Hand is "low" if it's at or below hip level
        left_hand_low = left_wrist_y > hip_y - 0.05  # Relaxed from -0.1
        right_hand_low = right_wrist_y > hip_y - 0.05
        # Hand is "very low" if clearly below hip (reaching toward ground)
        left_hand_very_low = left_wrist_y > hip_y + 0.05  # Relaxed from +0.1
        right_hand_very_low = right_wrist_y > hip_y + 0.05
        # Hand is "on ground" if very far down
        left_hand_ground = left_wrist_y > hip_y + 0.15
        right_hand_ground = right_wrist_y > hip_y + 0.15

        any_hand_low = left_hand_low or right_hand_low
        any_hand_very_low = left_hand_very_low or right_hand_very_low
        both_hands_low = left_hand_very_low and right_hand_very_low
        both_hands_ground = left_hand_ground and right_hand_ground
        one_hand_low = (left_hand_very_low and not right_hand_very_low) or \
                       (right_hand_very_low and not left_hand_very_low)
        one_hand_ground = (left_hand_ground and not right_hand_ground) or \
                          (right_hand_ground and not left_hand_ground)

        # Leg positions - MORE SENSITIVE thresholds
        # Leg is "raised" if ankle is higher than the other ankle
        ankle_diff = abs(left_ankle_y - right_ankle_y)
        left_leg_raised = left_ankle_y < right_ankle_y - 0.05  # Relaxed from -0.08
        right_leg_raised = right_ankle_y < left_ankle_y - 0.05
        any_leg_raised = ankle_diff > 0.05  # Relaxed from 0.08

        # High kick detection - ankle above knee or hip level
        left_leg_high = left_ankle_y < left_knee_y + 0.02  # Slightly more forgiving
        right_leg_high = right_ankle_y < right_knee_y + 0.02
        left_leg_very_high = left_ankle_y < hip_y + 0.05  # Slightly more forgiving
        right_leg_very_high = right_ankle_y < hip_y + 0.05
        any_leg_high = left_leg_high or right_leg_high
        any_leg_very_high = left_leg_very_high or right_leg_very_high

        # Body height (how low are the hips)
        body_standing = hip_y < 0.58  # Relaxed from 0.55
        body_crouching = hip_y >= 0.55 and hip_y < 0.78
        body_on_ground = hip_y >= 0.75

        # Leg extended (straight)
        left_leg_extended = left_knee_angle > 145  # Relaxed from 150
        right_leg_extended = right_knee_angle > 145

        # =================================================================
        # MOVEMENT DETECTION - Check specific movements FIRST
        # Priority: Kicks > Acrobatics > Ground > Defense > Ginga
        # =================================================================
        scores = {}

        # --- MEIA LUA DE COMPASSO (COMPASS KICK) - CHECK FIRST ---
        # Key: ONE hand reaching down/ground + leg raised/sweeping
        # This is a signature move - hand on ground, spinning kick
        if one_hand_ground and any_leg_raised:
            scores['meia_lua_de_compasso'] = 0.95
            scores['rabo_de_arraia'] = 0.88
        elif one_hand_low and any_leg_raised:
            scores['meia_lua_de_compasso'] = 0.92
            scores['rabo_de_arraia'] = 0.85
        elif one_hand_low and any_leg_high:
            scores['meia_lua_de_compasso'] = 0.90
            scores['rabo_de_arraia'] = 0.82
        elif any_hand_very_low and head_below_hips and any_leg_raised:
            scores['meia_lua_de_compasso'] = 0.88

        # --- AU (CARTWHEEL) ---
        # Key: Head below hips + BOTH hands low/on ground (not just one)
        if head_below_hips and both_hands_ground:
            scores['au'] = 0.95
            scores['bananeira'] = 0.88
        elif head_below_hips and both_hands_low:
            scores['au'] = 0.90
            if head_way_below_hips:
                scores['au'] = 0.93
                scores['bananeira'] = 0.85

        # --- ARMADA / HIGH KICKS ---
        # Key: Leg very high, no hands on ground, standing or slight crouch
        if any_leg_very_high and not any_hand_very_low and not head_below_hips:
            scores['armada'] = 0.92
            scores['meia_lua_de_frente'] = 0.87
            scores['martelo'] = 0.84
        elif any_leg_very_high and not both_hands_low:
            # Even if one hand is slightly low, could still be high kick
            scores['armada'] = 0.85
            scores['meia_lua_de_frente'] = 0.80

        # --- MARTELO / QUEIXADA / MEDIUM KICKS ---
        # Key: Leg raised above knee level, standing
        if any_leg_high and not any_leg_very_high and not any_hand_very_low:
            if body_standing:
                scores['martelo'] = 0.90
                scores['queixada'] = 0.87
                scores['armada'] = 0.82
            elif body_crouching:
                scores['martelo'] = 0.82
                scores['queixada'] = 0.80

        # --- BENCAO / CHAPA / FRONT KICKS ---
        # Key: Leg raised but extended forward, standing
        if any_leg_raised and (left_leg_extended or right_leg_extended) and body_standing:
            if 'armada' not in scores and 'martelo' not in scores:
                scores['bencao'] = 0.88
                scores['chapa'] = 0.82
                scores['ponteira'] = 0.78

        # --- ANY KICK (leg raised while standing) ---
        # Catch-all for kicks we might have missed
        if any_leg_raised and (body_standing or body_crouching) and not any_hand_very_low:
            if 'meia_lua_de_compasso' not in scores and 'armada' not in scores:
                if 'martelo' not in scores:
                    scores['martelo'] = 0.78
                if 'armada' not in scores:
                    scores['armada'] = 0.75
                if 'queixada' not in scores:
                    scores['queixada'] = 0.73

        # --- NEGATIVA ---
        # Key: Body very low/on ground + one leg extended
        if body_on_ground and (left_leg_extended or right_leg_extended):
            scores['negativa'] = 0.92
            scores['rasteira'] = 0.75
        elif body_crouching and (left_leg_extended or right_leg_extended) and any_hand_low:
            scores['negativa'] = 0.88
        elif body_on_ground:
            scores['negativa'] = 0.80  # Body low, likely negativa position

        # --- ROLE ---
        # Key: Body low + hands low + moving/transitioning
        if body_on_ground and any_hand_low and not (left_leg_extended and right_leg_extended):
            scores['role'] = 0.88
            if 'negativa' not in scores:
                scores['negativa'] = 0.72

        # --- ESQUIVA ---
        # Key: Crouching/low body, not on ground
        if body_crouching and not any_leg_raised and not any_leg_high:
            scores['esquiva_lateral'] = 0.85
            scores['esquiva_baixa'] = 0.82
            scores['cocorinha'] = 0.78

        # --- COCORINHA ---
        # Key: Very compact squat
        if body_crouching and left_knee_angle < 100 and right_knee_angle < 100:
            scores['cocorinha'] = 0.90
            scores['esquiva_baixa'] = 0.82

        # --- MACACO ---
        # Key: Crouching with hand reaching back, preparing for flip
        if body_crouching and any_hand_very_low and head_below_hips:
            scores['macaco'] = 0.78

        # --- GINGA (FALLBACK) ---
        # Only if standing normally with no other strong indicators
        if body_standing and not any_leg_high and not any_hand_very_low and not head_below_hips:
            if not scores:  # Only if nothing else detected
                scores['ginga'] = 0.82
            elif max(scores.values()) < 0.7:  # Weak detections
                scores['ginga'] = 0.50
            else:
                # Add ginga as low secondary possibility
                scores['ginga'] = 0.35

        # If still nothing, check for any slight leg movement
        if not scores:
            if any_leg_raised or ankle_diff > 0.03:
                scores['ginga'] = 0.72  # Some movement detected
            else:
                scores['ginga'] = 0.55  # Static standing

        # =================================================================
        # SELECT BEST MATCH
        # =================================================================
        if not scores:
            return self._unknown("Unable to classify movement")

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_match = sorted_scores[0]
        second_match = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)

        movement_info = self.MOVEMENTS.get(best_match[0], {})

        return DetectedMovement(
            movement_name=best_match[0],
            movement_name_pt=movement_info.get('name_pt', best_match[0]),
            category=movement_info.get('category', MovementCategory.UNKNOWN),
            confidence=best_match[1],
            description=movement_info.get('description', ''),
            secondary_guess=second_match[0] if second_match[1] > self.min_confidence else None,
            secondary_confidence=second_match[1]
        )

    def _unknown(self, reason: str) -> DetectedMovement:
        """Return unknown movement result."""
        return DetectedMovement(
            movement_name="unknown",
            movement_name_pt="Desconhecido",
            category=MovementCategory.UNKNOWN,
            confidence=0.0,
            description=reason
        )

    def detect_sequence(self, landmarks_sequence: List,
                       angles_sequence: List[Dict] = None) -> List[DetectedMovement]:
        """Detect movements across a sequence of frames."""
        results = []
        for i, landmarks in enumerate(landmarks_sequence):
            angles = angles_sequence[i] if angles_sequence else None
            results.append(self.detect(landmarks, angles))
        return results

    def get_dominant_movement(self, detections: List[DetectedMovement]) -> DetectedMovement:
        """Get the most commonly detected movement from a sequence."""
        if not detections:
            return self._unknown("No detections")

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
            return detections[0] if detections else self._unknown("No valid detections")

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
        return self.MOVEMENTS.copy()

    def get_movements_by_category(self, category: MovementCategory) -> List[str]:
        """Get all movements in a specific category."""
        return [name for name, info in self.MOVEMENTS.items()
                if info.get('category') == category]


def create_detector() -> MovementDetector:
    """Create and return a MovementDetector instance."""
    return MovementDetector()
