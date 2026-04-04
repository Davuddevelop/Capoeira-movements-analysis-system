"""
Esquiva Movement Scorer

Esquiva (dodge) is the primary defensive movement in capoeira.
Instead of blocking, capoeiristas evade by moving the head and torso
out of the attack trajectory.

TYPES OF ESQUIVA:
- Esquiva Lateral: Side dodge from ginga
- Esquiva Baixa: Low dodge dropping down
- Esquiva de Frente: Forward dodge
- Cocorinha: Squat dodge

BIOMECHANICAL BASIS:
- Deep knee flexion for low evasions (60-120°)
- Spine can lean significantly (90-160°)
- One hand often guards face
- Body compacts to reduce target area

Sources:
- DendeArts complete esquiva guide
- CapoeiraWiki movement descriptions
"""

from typing import List
from analyzer.movement_scorer import MovementScorer, AngleCriterion, create_criterion


class EsquivaScorer(MovementScorer):
    """
    Scores Esquiva (Dodge) movements.

    Esquiva is assessed on:
    1. Depth - how low the body goes (knee 60-130°)
    2. Compactness - reducing target area
    3. Head protection - hand guards face
    4. Balance - maintaining stability while evading

    Based on capoeira pedagogy and evasion principles.
    """

    # ================================================================
    # CALIBRATED VALUES - Based on esquiva technique
    # Deep knee flexion required for low evasions
    # Spine can lean significantly for lateral movement
    # ================================================================

    # Knee angles during esquiva (degrees)
    # Deep bend to get low and compact
    IDEAL_KNEE_MIN = 60   # Very deep esquiva (cocorinha)
    IDEAL_KNEE_MAX = 140  # Shallower lateral dodge

    # Hip angles (degrees)
    # Hip flexion during squat/dodge
    IDEAL_HIP_MIN = 50   # Deep squat position
    IDEAL_HIP_MAX = 150  # Entry/exit phases

    # Spine angle (degrees)
    # Can lean significantly for lateral movement
    IDEAL_SPINE_MIN = 90   # Significant lean allowed
    IDEAL_SPINE_MAX = 170  # More upright positions

    # Shoulder angle (degrees)
    # One arm guards face, other supports or guards
    IDEAL_SHOULDER_MIN = 30   # Arms active
    IDEAL_SHOULDER_MAX = 120  # Guarding position

    def _setup(self):
        """Set up esquiva-specific scoring criteria."""
        self.movement_name = "Esquiva"
        self.movement_name_pt = "Esquiva"
        self.description = (
            "Esquiva (dodge) is the primary defensive movement in capoeira. "
            "Instead of blocking attacks, the capoeirista moves the head and "
            "torso out of the attack trajectory. The body compacts to reduce "
            "the target area while maintaining readiness to counter."
        )

        self.criteria = [
            create_criterion(
                name="Left Knee Depth",
                angle_key="left_knee",
                ideal_min=self.IDEAL_KNEE_MIN,
                ideal_max=self.IDEAL_KNEE_MAX,
                weight=1.0,
                description="Deep knee bend for evasion (60-140°)"
            ),
            create_criterion(
                name="Right Knee Depth",
                angle_key="right_knee",
                ideal_min=self.IDEAL_KNEE_MIN,
                ideal_max=self.IDEAL_KNEE_MAX,
                weight=1.0,
                description="Deep knee bend for evasion (60-140°)"
            ),
            create_criterion(
                name="Left Hip Flexion",
                angle_key="left_hip",
                ideal_min=self.IDEAL_HIP_MIN,
                ideal_max=self.IDEAL_HIP_MAX,
                weight=0.9,
                description="Hip flexion for squat/dodge (50-150°)"
            ),
            create_criterion(
                name="Right Hip Flexion",
                angle_key="right_hip",
                ideal_min=self.IDEAL_HIP_MIN,
                ideal_max=self.IDEAL_HIP_MAX,
                weight=0.9,
                description="Hip flexion for squat/dodge (50-150°)"
            ),
            create_criterion(
                name="Spine Lean",
                angle_key="spine",
                ideal_min=self.IDEAL_SPINE_MIN,
                ideal_max=self.IDEAL_SPINE_MAX,
                weight=0.8,
                description="Lateral lean for evasion (90-170°)"
            ),
            create_criterion(
                name="Left Arm Guard",
                angle_key="left_shoulder",
                ideal_min=self.IDEAL_SHOULDER_MIN,
                ideal_max=self.IDEAL_SHOULDER_MAX,
                weight=0.7,
                description="Arm position for guard (30-120°)"
            ),
            create_criterion(
                name="Right Arm Guard",
                angle_key="right_shoulder",
                ideal_min=self.IDEAL_SHOULDER_MIN,
                ideal_max=self.IDEAL_SHOULDER_MAX,
                weight=0.7,
                description="Arm position for guard (30-120°)"
            ),
        ]

        self.common_mistakes = [
            "Not getting low enough - still in attack trajectory",
            "Eyes looking down instead of at opponent",
            "No hand guarding face - vulnerable to follow-up",
            "Losing balance during evasion",
            "Too slow - evasion must be quick",
            "Moving in wrong direction - into attack",
            "Not maintaining ready position for counter",
            "Legs too straight (>140°) - not enough depth",
            "Arms passive - should be actively guarding",
        ]

    def get_calibration_guide(self) -> str:
        """Returns biomechanical reference for esquiva technique."""
        return """
        ESQUIVA BIOMECHANICAL REFERENCE
        ================================

        CALIBRATED VALUES:
        - Knee angles: 60-140° (deep bend required)
        - Hip angles: 50-150° (varies with style)
        - Spine angle: 90-170° (significant lean allowed)
        - Shoulder angles: 30-120° (guarding position)

        ESQUIVA VARIANTS:
        1. Esquiva Lateral: Side dodge, chest to knee
        2. Esquiva Baixa: Deep low dodge, very low
        3. Cocorinha: Squat dodge, knees to chest
        4. Esquiva de Frente: Forward step dodge

        FLAWLESS EXECUTION:
        1. Quick reaction to incoming attack
        2. Body moves completely out of trajectory
        3. One hand guards face
        4. Eyes maintain opponent contact
        5. Ready to counter immediately

        Key principle: Avoid, don't block
        """


def create_esquiva_scorer() -> EsquivaScorer:
    """Create and return an EsquivaScorer instance."""
    return EsquivaScorer()
