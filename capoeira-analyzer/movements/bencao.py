"""
Bencao Movement Scorer

Bencao (blessing) is a front push kick aimed at the opponent's chest
or stomach. Despite the gentle name, it's a powerful pushing technique.

BIOMECHANICAL BASIS:
- Chamber phase: knee lifted and bent (~90°)
- Extension phase: leg extends straight forward (160-180°)
- Strike with sole of foot (heel) for pushing power
- Hip drives the kick, not just leg extension

Sources:
- CapoeiraWiki movement analysis
- Taekwondo front kick biomechanics research
"""

from typing import List
from analyzer.movement_scorer import MovementScorer, AngleCriterion, create_criterion


class BencaoScorer(MovementScorer):
    """
    Scores the Bencao (Front Push Kick) movement.

    The bencao is assessed on:
    1. Knee chamber - proper lift before extension (~90° bent)
    2. Leg extension - full extension at impact (155-180°)
    3. Hip drive - power comes from hip, not just leg
    4. Body posture - upright and balanced

    Based on front kick biomechanics research.
    """

    # ================================================================
    # CALIBRATED VALUES - Based on front kick biomechanics
    # Chamber: ~90-100° knee flexion
    # Extension: 155-180° (near-full to full)
    # ================================================================

    # Kicking leg knee at full extension (degrees)
    # Should be near-full to full extension at impact
    IDEAL_EXTENSION_KNEE_MIN = 155  # Near-full extension
    IDEAL_EXTENSION_KNEE_MAX = 180  # Full extension

    # Support leg knee (degrees)
    # Slight bend for stability during kick
    IDEAL_SUPPORT_KNEE_MIN = 130  # Stable bend
    IDEAL_SUPPORT_KNEE_MAX = 165  # Not locked

    # Hip angle during kick (degrees)
    # Hip drives the kick forward
    IDEAL_HIP_ANGLE_MIN = 70   # High kick position
    IDEAL_HIP_ANGLE_MAX = 150  # Lower kick or recovery

    # Spine angle (degrees)
    # Should be upright, slight backward lean acceptable
    IDEAL_SPINE_MIN = 150  # Slight lean OK for counterbalance
    IDEAL_SPINE_MAX = 180  # Upright

    # Ankle angle (degrees)
    # Foot should be flexed (dorsiflexed) to strike with heel
    IDEAL_ANKLE_MIN = 70   # Dorsiflexed for heel strike
    IDEAL_ANKLE_MAX = 110  # Range during kick

    def _setup(self):
        """Set up bencao-specific scoring criteria."""
        self.movement_name = "Bencao"
        self.movement_name_pt = "Bênção"
        self.description = (
            "Bencao (blessing) is a front push kick targeting the opponent's "
            "chest or stomach. The kick involves chambering the knee, then "
            "extending the leg straight forward with power from the hip. "
            "Strike with the sole of the foot (heel) for pushing power."
        )

        self.criteria = [
            create_criterion(
                name="Kicking Leg Extension",
                angle_key="left_knee",
                ideal_min=self.IDEAL_EXTENSION_KNEE_MIN,
                ideal_max=self.IDEAL_EXTENSION_KNEE_MAX,
                weight=1.0,
                description="Full extension at impact (155-180°)"
            ),
            create_criterion(
                name="Support Leg Stability",
                angle_key="right_knee",
                ideal_min=self.IDEAL_SUPPORT_KNEE_MIN,
                ideal_max=self.IDEAL_SUPPORT_KNEE_MAX,
                weight=1.0,
                description="Bent for stability (130-165°)"
            ),
            create_criterion(
                name="Kicking Hip Drive",
                angle_key="left_hip",
                ideal_min=self.IDEAL_HIP_ANGLE_MIN,
                ideal_max=self.IDEAL_HIP_ANGLE_MAX,
                weight=1.0,
                description="Hip drives the kick (70-150°)"
            ),
            create_criterion(
                name="Support Hip Angle",
                angle_key="right_hip",
                ideal_min=self.IDEAL_HIP_ANGLE_MIN,
                ideal_max=self.IDEAL_HIP_ANGLE_MAX,
                weight=0.8,
                description="Hip stability"
            ),
            create_criterion(
                name="Spine Alignment",
                angle_key="spine",
                ideal_min=self.IDEAL_SPINE_MIN,
                ideal_max=self.IDEAL_SPINE_MAX,
                weight=0.9,
                description="Upright posture (150-180°)"
            ),
            create_criterion(
                name="Kicking Foot Position",
                angle_key="left_ankle",
                ideal_min=self.IDEAL_ANKLE_MIN,
                ideal_max=self.IDEAL_ANKLE_MAX,
                weight=0.7,
                description="Flexed for heel strike (70-110°)"
            ),
        ]

        self.common_mistakes = [
            "No chamber - extending without lifting knee first",
            "Bent knee at impact - should be near-straight (>155°)",
            "Excessive backward lean (spine <150°)",
            "Pointed toes instead of flexed foot for heel strike",
            "Support leg locked (>165°) - needs slight bend",
            "Kick too low or too high - target chest/stomach",
            "Using leg only - power should come from hip",
            "Losing balance after kick",
            "Arms not guarding during kick",
            "Slow retraction - leg should snap back quickly",
        ]

    def get_calibration_guide(self) -> str:
        """Returns biomechanical reference for bencao technique."""
        return """
        BENCAO BIOMECHANICAL REFERENCE
        ==============================

        CALIBRATED VALUES:
        - Kicking knee (impact): 155-180° (near-full extension)
        - Support knee: 130-165° (bent for stability)
        - Hip angle: 70-150° (varies with kick height)
        - Spine: 150-180° (upright, slight lean OK)
        - Ankle: 70-110° (dorsiflexed for heel strike)

        CHAMBER PHASE (not directly measured):
        - Knee lifted to hip height
        - Knee bent ~90° before extension

        FLAWLESS EXECUTION CRITERIA:
        1. Clear chamber before extension
        2. Full leg extension at impact
        3. Power from hip thrust, not just leg
        4. Strike with sole/heel of foot
        5. Quick retraction after impact
        6. Maintain balance throughout

        Target: chest or stomach level
        """


def create_bencao_scorer() -> BencaoScorer:
    """Create and return a BencaoScorer instance."""
    return BencaoScorer()
