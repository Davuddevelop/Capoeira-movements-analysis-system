"""
Meia-lua de Frente Movement Scorer

Meia-lua de frente (half-moon from the front) is an outside crescent kick
that sweeps across the opponent's face in a semicircular arc.

BIOMECHANICAL BASIS:
- Circular motion from outside to inside
- Leg travels in arc at head height
- Strike with outer edge or instep of foot
- Balance maintained on support leg throughout

Sources:
- CapoeiraWiki movement descriptions
- PMC5571909: Kick biomechanics research
"""

from typing import List
from analyzer.movement_scorer import MovementScorer, AngleCriterion, create_criterion


class MeiaLuaScorer(MovementScorer):
    """
    Scores the Meia-lua de Frente (Half-Moon Kick) movement.

    The meia-lua de frente is assessed on:
    1. Kicking leg extension - full extension at peak (150-180°)
    2. Support leg stability - slight bend for balance (130-165°)
    3. Hip rotation - proper arc of the kick (80-160°)
    4. Body alignment - torso position during kick

    Based on biomechanical research on crescent kicks.
    """

    # ================================================================
    # CALIBRATED VALUES - Based on biomechanical research
    # Crescent kicks require full leg extension at arc peak
    # ================================================================

    # Kicking leg knee angle at peak (degrees)
    # Should be mostly straight at peak of arc
    IDEAL_KICK_KNEE_MIN = 150  # Near straight
    IDEAL_KICK_KNEE_MAX = 180  # Full extension

    # Support leg knee angle (degrees)
    # Slight bend maintains balance during arc
    IDEAL_SUPPORT_KNEE_MIN = 130  # Stable bend
    IDEAL_SUPPORT_KNEE_MAX = 165  # Not too straight

    # Hip angle during kick (degrees)
    # Hip flexion varies through the arc
    IDEAL_KICK_HIP_MIN = 80   # During high arc
    IDEAL_KICK_HIP_MAX = 165  # Entry/exit phases

    # Spine angle (degrees)
    # Torso may lean slightly away for balance
    IDEAL_SPINE_MIN = 140  # Slight counterlean OK
    IDEAL_SPINE_MAX = 180  # Upright

    # Ankle angle (degrees)
    # Support foot stability
    IDEAL_ANKLE_MIN = 70   # Flexed for stability
    IDEAL_ANKLE_MAX = 120  # Normal range

    def _setup(self):
        """Set up meia-lua de frente specific scoring criteria."""
        self.movement_name = "Meia-lua de Frente"
        self.movement_name_pt = "Meia-lua de Frente"
        self.description = (
            "Meia-lua de frente (half-moon from the front) is an outside "
            "crescent kick that sweeps across the opponent's face. The leg "
            "travels in a semicircular arc from outside to inside, striking "
            "with the outer edge or instep of the foot."
        )

        self.criteria = [
            create_criterion(
                name="Kicking Leg Extension",
                angle_key="left_knee",
                ideal_min=self.IDEAL_KICK_KNEE_MIN,
                ideal_max=self.IDEAL_KICK_KNEE_MAX,
                weight=1.0,
                description="Full extension at arc peak (150-180°)"
            ),
            create_criterion(
                name="Support Leg Stability",
                angle_key="right_knee",
                ideal_min=self.IDEAL_SUPPORT_KNEE_MIN,
                ideal_max=self.IDEAL_SUPPORT_KNEE_MAX,
                weight=1.0,
                description="Bent for balance (130-165°)"
            ),
            create_criterion(
                name="Kicking Hip Arc",
                angle_key="left_hip",
                ideal_min=self.IDEAL_KICK_HIP_MIN,
                ideal_max=self.IDEAL_KICK_HIP_MAX,
                weight=1.0,
                description="Hip angle for kick height (80-165°)"
            ),
            create_criterion(
                name="Support Hip Angle",
                angle_key="right_hip",
                ideal_min=self.IDEAL_KICK_HIP_MIN,
                ideal_max=self.IDEAL_KICK_HIP_MAX,
                weight=0.8,
                description="Hip stability during kick"
            ),
            create_criterion(
                name="Spine Alignment",
                angle_key="spine",
                ideal_min=self.IDEAL_SPINE_MIN,
                ideal_max=self.IDEAL_SPINE_MAX,
                weight=0.9,
                description="Torso balance (140-180°)"
            ),
            create_criterion(
                name="Support Ankle",
                angle_key="right_ankle",
                ideal_min=self.IDEAL_ANKLE_MIN,
                ideal_max=self.IDEAL_ANKLE_MAX,
                weight=0.7,
                description="Foot stability (70-120°)"
            ),
        ]

        self.common_mistakes = [
            "Bent knee at arc peak - should be straight (>150°)",
            "Kick too low - should target head height",
            "Support leg locked (>165°) - needs slight bend",
            "Losing balance during kick arc",
            "Incomplete arc - not following through",
            "Excessive torso lean (spine <140°)",
            "Kicking with shin instead of foot",
            "Telegraphing - too much preparation visible",
            "Slow arc - lacking hip power",
        ]

    def get_calibration_guide(self) -> str:
        """Returns biomechanical reference for meia-lua technique."""
        return """
        MEIA-LUA DE FRENTE BIOMECHANICAL REFERENCE
        ==========================================

        CALIBRATED VALUES:
        - Kicking knee: 150-180° (full extension at peak)
        - Support knee: 130-165° (bent for stability)
        - Hip angle: 80-165° (varies through arc)
        - Spine: 140-180° (slight counterlean OK)
        - Support ankle: 70-120° (stable base)

        FLAWLESS EXECUTION CRITERIA:
        1. Complete semicircular arc at head height
        2. Full leg extension at arc peak
        3. Smooth continuous motion
        4. Balance maintained throughout
        5. Clean return to ginga

        Strike surface: outer edge or instep of foot
        """


def create_meia_lua_scorer() -> MeiaLuaScorer:
    """Create and return a MeiaLuaScorer instance."""
    return MeiaLuaScorer()
