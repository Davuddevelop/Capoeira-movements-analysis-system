"""
Martelo Movement Scorer

Martelo (hammer) is capoeira's roundhouse kick, striking with the
instep or lower shin. One of the most powerful kicks when properly
executed with hip rotation.

BIOMECHANICAL BASIS (PMC5571909):
- Maximum knee flexion ~96-99° during chamber
- Knee extension 15-43° at impact (discipline varies)
- Hip flexion 25-39° at impact
- Hip abduction ~50-53°
- Pelvis rotation ~92-122°

Sources:
- PMC5571909: Roundhouse kick biomechanics
- CapoeiraWiki movement descriptions
"""

from typing import List
from analyzer.movement_scorer import MovementScorer, AngleCriterion, create_criterion


class MarteloScorer(MovementScorer):
    """
    Scores the Martelo (Roundhouse Kick) movement.

    Based directly on PMC5571909 biomechanical research:
    1. Knee extension at impact - varies by style (137-165°)
    2. Support leg stability - bent for balance (130-160°)
    3. Hip rotation - pelvis drives the kick
    4. Hip abduction - leg travels laterally

    Research-calibrated values from martial arts biomechanics study.
    """

    # ================================================================
    # CALIBRATED VALUES - Based on PMC5571909 research
    # Muay Thai: 43° flexion at impact (137° extension)
    # Karate/TKD: 15-16° flexion (164-165° extension)
    # Capoeira closer to Karate/TKD style
    # ================================================================

    # Kicking leg knee at impact (degrees)
    # Research: 15-43° flexion = 137-165° extension
    # Capoeira typically aims for more extension
    IDEAL_KICK_KNEE_MIN = 145  # Some flex acceptable
    IDEAL_KICK_KNEE_MAX = 175  # Near-full extension

    # Support leg knee (degrees)
    # Research: bent support leg is good form
    IDEAL_SUPPORT_KNEE_MIN = 130  # Good bend
    IDEAL_SUPPORT_KNEE_MAX = 160  # Not locked

    # Hip angles (degrees)
    # Research: 25-39° flexion at impact
    # Plus hip abduction ~50-53°
    IDEAL_HIP_MIN = 70   # Varies through kick
    IDEAL_HIP_MAX = 160  # Entry/exit phases

    # Spine angle (degrees)
    # Body rotates with kick
    IDEAL_SPINE_MIN = 140  # Rotation lean
    IDEAL_SPINE_MAX = 180  # Upright recovery

    # Shoulder angle (degrees)
    # Arms guard and counter-rotate
    IDEAL_SHOULDER_MIN = 30   # Guard position
    IDEAL_SHOULDER_MAX = 100  # Active guard

    def _setup(self):
        """Set up martelo-specific scoring criteria."""
        self.movement_name = "Martelo"
        self.movement_name_pt = "Martelo"
        self.description = (
            "Martelo (hammer) is capoeira's roundhouse kick. The leg swings "
            "in a horizontal arc, striking with the instep or lower shin. "
            "Power comes from hip rotation - the pelvis drives the kick. "
            "One of the most powerful kicks when properly executed."
        )

        self.criteria = [
            create_criterion(
                name="Kicking Leg Extension",
                angle_key="left_knee",
                ideal_min=self.IDEAL_KICK_KNEE_MIN,
                ideal_max=self.IDEAL_KICK_KNEE_MAX,
                weight=1.0,
                description="Near-full extension (145-175°)"
            ),
            create_criterion(
                name="Support Leg Stability",
                angle_key="right_knee",
                ideal_min=self.IDEAL_SUPPORT_KNEE_MIN,
                ideal_max=self.IDEAL_SUPPORT_KNEE_MAX,
                weight=1.0,
                description="Bent for stability (130-160°)"
            ),
            create_criterion(
                name="Kicking Hip Drive",
                angle_key="left_hip",
                ideal_min=self.IDEAL_HIP_MIN,
                ideal_max=self.IDEAL_HIP_MAX,
                weight=1.0,
                description="Hip rotation power (70-160°)"
            ),
            create_criterion(
                name="Support Hip Position",
                angle_key="right_hip",
                ideal_min=self.IDEAL_HIP_MIN,
                ideal_max=self.IDEAL_HIP_MAX,
                weight=0.8,
                description="Hip pivot and rotation"
            ),
            create_criterion(
                name="Body Rotation",
                angle_key="spine",
                ideal_min=self.IDEAL_SPINE_MIN,
                ideal_max=self.IDEAL_SPINE_MAX,
                weight=0.9,
                description="Torso rotation (140-180°)"
            ),
            create_criterion(
                name="Left Arm Guard",
                angle_key="left_shoulder",
                ideal_min=self.IDEAL_SHOULDER_MIN,
                ideal_max=self.IDEAL_SHOULDER_MAX,
                weight=0.6,
                description="Guard and counter-rotate (30-100°)"
            ),
            create_criterion(
                name="Right Arm Guard",
                angle_key="right_shoulder",
                ideal_min=self.IDEAL_SHOULDER_MIN,
                ideal_max=self.IDEAL_SHOULDER_MAX,
                weight=0.6,
                description="Guard and counter-rotate (30-100°)"
            ),
        ]

        self.common_mistakes = [
            "Knee too bent at impact (<145°) - Muay Thai style",
            "Support leg locked (>160°) - reduces stability",
            "No hip rotation - using leg only, no power",
            "Kicking with toes - should use instep/shin",
            "Excessive forward lean (spine <140°)",
            "Kick too low - should target head/ribs",
            "Arms passive - not guarding",
            "No chamber - leg swings from ground",
            "Slow kick - lacks hip velocity",
        ]

    def get_calibration_guide(self) -> str:
        """Returns biomechanical reference for martelo technique."""
        return """
        MARTELO BIOMECHANICAL REFERENCE (PMC5571909)
        =============================================

        RESEARCH-BASED VALUES:
        - Kicking knee at impact:
          * Muay Thai: 137° (43° flexion) - more bent
          * Karate: 165° (15° flexion) - straighter
          * Taekwondo: 164° (16° flexion) - straighter
          * Capoeira target: 145-175°

        - Support knee: 130-160° (bent for stability)
        - Hip flexion: 25-39° at impact
        - Hip abduction: 50-53° at impact
        - Pelvis rotation: 92-122° range of motion

        CHAMBER PHASE:
        - Knee flexion: ~96-99° (research consensus)

        FLAWLESS EXECUTION:
        1. Clear chamber before extension
        2. Hip rotation drives the kick
        3. Full leg extension at impact
        4. Strike with instep or shin
        5. Support leg bent, pivoting

        Source: PMC5571909 - Roundhouse kick biomechanics
        """


def create_martelo_scorer() -> MarteloScorer:
    """Create and return a MarteloScorer instance."""
    return MarteloScorer()
