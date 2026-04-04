"""
Negativa Movement Scorer

Negativa is a ground-level defensive position where one leg extends
while the other is bent underneath. It's both an evasion and a
transition position for sweeps and ground attacks.

TYPES:
- Negativa de Angola: Very low, close to ground
- Negativa de Bimba/Regional: Slightly higher, more mobile
- Negativa Derrubando: Negativa used as a sweep

BIOMECHANICAL BASIS:
- One leg fully extended (160-180°)
- Other leg deeply bent underneath (40-80°)
- Torso very low, often supported by hands
- Eyes maintain opponent contact

Sources:
- DendeArts negativa guide
- CapoeiraWiki movement descriptions
"""

from typing import List
from analyzer.movement_scorer import MovementScorer, AngleCriterion, create_criterion


class NegativaScorer(MovementScorer):
    """
    Scores the Negativa (Ground Evasion) movement.

    Negativa is assessed on:
    1. Extended leg - straight extension (155-180°)
    2. Bent leg - deep flexion underneath (40-100°)
    3. Low body position - close to ground
    4. Hand support - proper positioning

    Based on capoeira ground movement principles.
    """

    # ================================================================
    # CALIBRATED VALUES - Based on negativa technique
    # One leg extended, one deeply bent
    # Body very low, near ground level
    # ================================================================

    # Extended leg knee angle (degrees)
    # Should be straight or nearly straight
    IDEAL_EXTENDED_KNEE_MIN = 155  # Near straight
    IDEAL_EXTENDED_KNEE_MAX = 180  # Full extension

    # Bent leg knee angle (degrees)
    # Deep flexion underneath body
    IDEAL_BENT_KNEE_MIN = 40   # Very deep bend
    IDEAL_BENT_KNEE_MAX = 100  # Moderately bent

    # Hip angles (degrees)
    # Varies significantly between extended and bent side
    IDEAL_HIP_MIN = 40   # Very low position
    IDEAL_HIP_MAX = 160  # Extended side

    # Spine angle (degrees)
    # Body low, can be quite angled
    IDEAL_SPINE_MIN = 70   # Very low angle
    IDEAL_SPINE_MAX = 150  # More upright variant

    # Shoulder angle (degrees)
    # Arms support body or guard
    IDEAL_SHOULDER_MIN = 60   # Supporting position
    IDEAL_SHOULDER_MAX = 150  # Reaching to ground

    def _setup(self):
        """Set up negativa-specific scoring criteria."""
        self.movement_name = "Negativa"
        self.movement_name_pt = "Negativa"
        self.description = (
            "Negativa is a ground-level defensive position combining evasion "
            "with sweep potential. One leg extends while the other bends "
            "underneath. The body is very low, often supported by hands. "
            "It's both a defensive position and a base for ground attacks."
        )

        self.criteria = [
            create_criterion(
                name="Extended Leg",
                angle_key="left_knee",
                ideal_min=self.IDEAL_EXTENDED_KNEE_MIN,
                ideal_max=self.IDEAL_EXTENDED_KNEE_MAX,
                weight=1.0,
                description="Leg fully extended (155-180°)"
            ),
            create_criterion(
                name="Bent Leg",
                angle_key="right_knee",
                ideal_min=self.IDEAL_BENT_KNEE_MIN,
                ideal_max=self.IDEAL_BENT_KNEE_MAX,
                weight=1.0,
                description="Leg deeply bent underneath (40-100°)"
            ),
            create_criterion(
                name="Extended Hip",
                angle_key="left_hip",
                ideal_min=self.IDEAL_HIP_MIN,
                ideal_max=self.IDEAL_HIP_MAX,
                weight=0.9,
                description="Hip position for extension (40-160°)"
            ),
            create_criterion(
                name="Bent Hip",
                angle_key="right_hip",
                ideal_min=self.IDEAL_HIP_MIN,
                ideal_max=self.IDEAL_HIP_MAX,
                weight=0.9,
                description="Hip flexion for bent leg"
            ),
            create_criterion(
                name="Body Angle",
                angle_key="spine",
                ideal_min=self.IDEAL_SPINE_MIN,
                ideal_max=self.IDEAL_SPINE_MAX,
                weight=0.8,
                description="Low body position (70-150°)"
            ),
            create_criterion(
                name="Left Arm Support",
                angle_key="left_shoulder",
                ideal_min=self.IDEAL_SHOULDER_MIN,
                ideal_max=self.IDEAL_SHOULDER_MAX,
                weight=0.7,
                description="Arm supporting/guarding (60-150°)"
            ),
            create_criterion(
                name="Right Arm Support",
                angle_key="right_shoulder",
                ideal_min=self.IDEAL_SHOULDER_MIN,
                ideal_max=self.IDEAL_SHOULDER_MAX,
                weight=0.7,
                description="Arm supporting/guarding (60-150°)"
            ),
        ]

        self.common_mistakes = [
            "Extended leg not straight enough (<155°)",
            "Bent leg not deep enough (>100°)",
            "Body too high - should be very low to ground",
            "Eyes looking down instead of at opponent",
            "No hand support - unstable position",
            "Extended leg in wrong direction",
            "Unable to transition to sweep or escape",
            "Losing balance in position",
            "Exposed to follow-up attacks",
        ]

    def get_calibration_guide(self) -> str:
        """Returns biomechanical reference for negativa technique."""
        return """
        NEGATIVA BIOMECHANICAL REFERENCE
        =================================

        CALIBRATED VALUES:
        - Extended leg knee: 155-180° (straight)
        - Bent leg knee: 40-100° (deep flexion)
        - Hip angles: 40-160° (asymmetric)
        - Spine angle: 70-150° (low position)
        - Shoulder angles: 60-150° (support/guard)

        NEGATIVA VARIANTS:
        1. Negativa de Angola: Lowest, hands perpendicular
        2. Negativa de Bimba: Higher, more mobile
        3. Negativa Derrubando: Used as sweep

        FLAWLESS EXECUTION:
        1. One leg fully extended, one deeply bent
        2. Body very close to ground
        3. Hands support and protect
        4. Eyes maintain opponent contact
        5. Ready to sweep or escape
        """


def create_negativa_scorer() -> NegativaScorer:
    """Create and return a NegativaScorer instance."""
    return NegativaScorer()
