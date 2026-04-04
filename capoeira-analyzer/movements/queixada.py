"""
Queixada Movement Scorer

Queixada is an inside-to-outside crescent kick, the reverse of meia-lua.
The leg travels in an arc from inside to outside, striking with the
outer edge of the foot.

BIOMECHANICAL BASIS:
- Circular motion from inside to outside
- Full leg extension at arc peak
- Strike with outer edge of foot
- Body rotates opposite to kick direction
- Often used as counter-attack or esquiva combo

Sources:
- CapoeiraWiki movement descriptions
- PMC5571909: Kick biomechanics research
"""

from typing import List
from analyzer.movement_scorer import MovementScorer, AngleCriterion, create_criterion


class QueixadaScorer(MovementScorer):
    """
    Scores the Queixada (Inside Crescent Kick) movement.

    Queixada is assessed on:
    1. Kicking leg extension - full at peak (150-180°)
    2. Support leg stability - bent for balance (125-160°)
    3. Hip rotation - drives the arc outward
    4. Body rotation - counter-rotates for power

    Based on crescent kick biomechanics.
    """

    # ================================================================
    # CALIBRATED VALUES - Based on crescent kick biomechanics
    # Similar to meia-lua but in reverse direction
    # ================================================================

    # Kicking leg knee at peak (degrees)
    # Full extension at arc peak
    IDEAL_KICK_KNEE_MIN = 150  # Near straight
    IDEAL_KICK_KNEE_MAX = 180  # Full extension

    # Support leg knee (degrees)
    # Bent for stability during arc
    IDEAL_SUPPORT_KNEE_MIN = 125  # Good bend
    IDEAL_SUPPORT_KNEE_MAX = 165  # Not locked

    # Hip angle (degrees)
    # Hip rotation drives the kick outward
    IDEAL_HIP_MIN = 80   # High kick position
    IDEAL_HIP_MAX = 165  # Entry/exit

    # Spine angle (degrees)
    # Body may rotate and lean for power
    IDEAL_SPINE_MIN = 135  # Counter-rotation lean
    IDEAL_SPINE_MAX = 180  # Upright

    # Shoulder angle (degrees)
    # Arms counter-rotate for power
    IDEAL_SHOULDER_MIN = 30   # Active position
    IDEAL_SHOULDER_MAX = 110  # Counter-rotation

    def _setup(self):
        """Set up queixada-specific scoring criteria."""
        self.movement_name = "Queixada"
        self.movement_name_pt = "Queixada"
        self.description = (
            "Queixada is an inside-to-outside crescent kick, the reverse of "
            "meia-lua de frente. The leg travels from inside to outside in "
            "an arc, striking with the outer edge of the foot. Often used "
            "as a counter-attack combined with esquiva."
        )

        self.criteria = [
            create_criterion(
                name="Kicking Leg Extension",
                angle_key="left_knee",
                ideal_min=self.IDEAL_KICK_KNEE_MIN,
                ideal_max=self.IDEAL_KICK_KNEE_MAX,
                weight=1.0,
                description="Full extension at peak (150-180°)"
            ),
            create_criterion(
                name="Support Leg Stability",
                angle_key="right_knee",
                ideal_min=self.IDEAL_SUPPORT_KNEE_MIN,
                ideal_max=self.IDEAL_SUPPORT_KNEE_MAX,
                weight=1.0,
                description="Bent for balance (125-165°)"
            ),
            create_criterion(
                name="Kicking Hip Arc",
                angle_key="left_hip",
                ideal_min=self.IDEAL_HIP_MIN,
                ideal_max=self.IDEAL_HIP_MAX,
                weight=1.0,
                description="Hip drives kick outward (80-165°)"
            ),
            create_criterion(
                name="Support Hip",
                angle_key="right_hip",
                ideal_min=self.IDEAL_HIP_MIN,
                ideal_max=self.IDEAL_HIP_MAX,
                weight=0.8,
                description="Hip stability"
            ),
            create_criterion(
                name="Body Rotation",
                angle_key="spine",
                ideal_min=self.IDEAL_SPINE_MIN,
                ideal_max=self.IDEAL_SPINE_MAX,
                weight=0.9,
                description="Counter-rotation (135-180°)"
            ),
            create_criterion(
                name="Left Arm Position",
                angle_key="left_shoulder",
                ideal_min=self.IDEAL_SHOULDER_MIN,
                ideal_max=self.IDEAL_SHOULDER_MAX,
                weight=0.6,
                description="Counter-rotation (30-110°)"
            ),
            create_criterion(
                name="Right Arm Position",
                angle_key="right_shoulder",
                ideal_min=self.IDEAL_SHOULDER_MIN,
                ideal_max=self.IDEAL_SHOULDER_MAX,
                weight=0.6,
                description="Counter-rotation (30-110°)"
            ),
        ]

        self.common_mistakes = [
            "Bent knee at peak - should be straight (>150°)",
            "Kick too low - should target head height",
            "Support leg locked (>165°)",
            "Arc incomplete - not following through",
            "No body counter-rotation - reduces power",
            "Losing balance during arc",
            "Wrong strike surface - should be outer edge",
            "Telegraphing - too much preparation visible",
        ]

    def get_calibration_guide(self) -> str:
        """Returns biomechanical reference for queixada technique."""
        return """
        QUEIXADA BIOMECHANICAL REFERENCE
        =================================

        CALIBRATED VALUES:
        - Kicking knee: 150-180° (full extension at peak)
        - Support knee: 125-165° (bent for stability)
        - Hip angle: 80-165° (drives outward arc)
        - Spine: 135-180° (allows counter-rotation)
        - Shoulders: 30-110° (counter-rotation)

        KEY DIFFERENCES FROM MEIA-LUA:
        - Arc direction: inside to outside (vs outside to inside)
        - Body counter-rotates for power
        - Often used as counter-attack

        FLAWLESS EXECUTION:
        1. Arc from inside to outside
        2. Full leg extension at peak
        3. Body counter-rotates for power
        4. Strike with outer edge of foot
        5. Smooth return to ginga
        """


def create_queixada_scorer() -> QueixadaScorer:
    """Create and return a QueixadaScorer instance."""
    return QueixadaScorer()
