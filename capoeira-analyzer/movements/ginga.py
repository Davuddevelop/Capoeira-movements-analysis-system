"""
Ginga Movement Scorer

Ginga is the fundamental movement of capoeira - a continuous side-to-side
weight shifting movement that serves as the base for all other movements.

The ginga involves:
- Rhythmic weight transfer from one leg to the other
- Maintaining a low center of gravity with bent knees
- Upper body remains relatively upright but fluid
- Arms move in opposition to the legs for balance

BIOMECHANICAL BASIS:
Research shows bent-knee stances reduce joint impact by 40% versus upright
stances. The ginga's triangular footwork creates constant motion while
maintaining balance and readiness for attacks or evasions.

Sources:
- Motion capture analysis of capoeira ginga (Academia.edu)
- ResearchGate study on ginga foot placement patterns
"""

from typing import List
from analyzer.movement_scorer import MovementScorer, AngleCriterion, create_criterion


class GingaScorer(MovementScorer):
    """
    Scores the Ginga movement - the fundamental capoeira movement.

    The ginga is assessed on:
    1. Knee bend depth - proper athletic stance (120-160°)
    2. Hip angle - weight distribution (140-175°)
    3. Spine angle - torso posture (155-180°)
    4. Arm position - guard and balance

    Scoring based on biomechanical research and capoeira pedagogy.
    """

    # ================================================================
    # CALIBRATED VALUES - Based on biomechanical research
    # Bent-knee ginga reduces joint impact by 40% vs upright stances
    # ================================================================

    # Knee angles during ginga (degrees)
    # Athletic stance requires moderate knee bend
    # 180° = straight leg, lower values = more bent
    IDEAL_KNEE_BEND_MIN = 115  # Minimum bend (not too deep)
    IDEAL_KNEE_BEND_MAX = 165  # Maximum (not too straight)

    # Hip angles (degrees)
    # Hip angle varies as weight shifts between legs
    # Should maintain relatively open hip for mobility
    IDEAL_HIP_ANGLE_MIN = 140  # During weight shift
    IDEAL_HIP_ANGLE_MAX = 175  # Near standing position

    # Spine/torso angle (degrees)
    # Torso should be relatively upright with slight forward lean allowed
    # 180° = perfectly vertical
    IDEAL_SPINE_ANGLE_MIN = 155  # Slight lean acceptable
    IDEAL_SPINE_ANGLE_MAX = 180  # Upright

    # Shoulder angle (arms position for guard)
    # Arms should be active, not hanging at sides
    IDEAL_SHOULDER_ANGLE_MIN = 25   # Arms somewhat raised
    IDEAL_SHOULDER_ANGLE_MAX = 90   # Not above shoulder height

    def _setup(self):
        """Set up ginga-specific scoring criteria."""
        self.movement_name = "Ginga"
        self.movement_name_pt = "Ginga"
        self.description = (
            "The ginga is the fundamental movement of capoeira. It involves "
            "continuous side-to-side weight shifting with a rhythmic pattern. "
            "The capoeirista maintains a low athletic stance while moving "
            "fluidly between positions. The triangular footwork confuses "
            "opponents while preparing for attacks or evasions."
        )

        # Define scoring criteria with calibrated values
        self.criteria = [
            create_criterion(
                name="Left Knee Bend",
                angle_key="left_knee",
                ideal_min=self.IDEAL_KNEE_BEND_MIN,
                ideal_max=self.IDEAL_KNEE_BEND_MAX,
                weight=1.0,
                description="Knee bend depth for athletic stance (115-165°)"
            ),
            create_criterion(
                name="Right Knee Bend",
                angle_key="right_knee",
                ideal_min=self.IDEAL_KNEE_BEND_MIN,
                ideal_max=self.IDEAL_KNEE_BEND_MAX,
                weight=1.0,
                description="Knee bend depth for athletic stance (115-165°)"
            ),
            create_criterion(
                name="Left Hip Angle",
                angle_key="left_hip",
                ideal_min=self.IDEAL_HIP_ANGLE_MIN,
                ideal_max=self.IDEAL_HIP_ANGLE_MAX,
                weight=0.8,
                description="Hip angle for weight distribution (140-175°)"
            ),
            create_criterion(
                name="Right Hip Angle",
                angle_key="right_hip",
                ideal_min=self.IDEAL_HIP_ANGLE_MIN,
                ideal_max=self.IDEAL_HIP_ANGLE_MAX,
                weight=0.8,
                description="Hip angle for weight distribution (140-175°)"
            ),
            create_criterion(
                name="Spine Posture",
                angle_key="spine",
                ideal_min=self.IDEAL_SPINE_ANGLE_MIN,
                ideal_max=self.IDEAL_SPINE_ANGLE_MAX,
                weight=1.0,
                description="Torso should be upright (155-180°)"
            ),
            create_criterion(
                name="Left Arm Guard",
                angle_key="left_shoulder",
                ideal_min=self.IDEAL_SHOULDER_ANGLE_MIN,
                ideal_max=self.IDEAL_SHOULDER_ANGLE_MAX,
                weight=0.6,
                description="Arms active for guard and balance (25-90°)"
            ),
            create_criterion(
                name="Right Arm Guard",
                angle_key="right_shoulder",
                ideal_min=self.IDEAL_SHOULDER_ANGLE_MIN,
                ideal_max=self.IDEAL_SHOULDER_ANGLE_MAX,
                weight=0.6,
                description="Arms active for guard and balance (25-90°)"
            ),
        ]

        self.common_mistakes = [
            "Standing too upright - not bending knees enough (>165°)",
            "Squatting too deep - overcommitting (<115°)",
            "Leaning too far forward (spine <155°)",
            "Not transferring weight fully between legs",
            "Arms hanging at sides - should be active guard",
            "Looking down instead of at opponent/partner",
            "Feet too close together - reduces stability",
            "Feet too far apart - reduces mobility",
            "Moving without rhythm - should sync to music",
            "Stiff upper body - should flow naturally",
        ]

    def get_calibration_guide(self) -> str:
        """Returns biomechanical reference guide for ginga technique."""
        return """
        GINGA BIOMECHANICAL REFERENCE
        =============================

        CURRENT CALIBRATED VALUES:
        - Knee bend: 115-165° (athletic stance)
        - Hip angle: 140-175° (weight distribution)
        - Spine angle: 155-180° (upright posture)
        - Shoulder angle: 25-90° (active guard)

        KEY BIOMECHANICAL PRINCIPLES:
        1. Bent-knee stance reduces joint impact by 40%
        2. Triangular footwork creates constant motion
        3. Weight shifts between front and back foot
        4. Arms move in opposition for balance

        PERFECT FORM INDICATORS:
        - Smooth, rhythmic weight transfer
        - Head stays level during movement
        - Eyes forward, watching opponent
        - Ball of back foot maintains contact
        - Front foot bears majority of weight

        ADJUSTMENT NOTES:
        - For Regional style: slightly more upright (160-180°)
        - For Angola style: deeper stance (110-150°)

        Contact: Azerbaijan Capoeira Federation
        """


def create_ginga_scorer() -> GingaScorer:
    """Create and return a GingaScorer instance."""
    return GingaScorer()
