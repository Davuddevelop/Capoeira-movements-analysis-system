"""
Au (Cartwheel) Movement Scorer

Au is the capoeira cartwheel - a fundamental acrobatic movement used
for evasion, repositioning, and as a base for many other techniques.

BIOMECHANICAL BASIS:
- Arms support full body weight during rotation
- Legs spread wide and straight during peak
- Eyes maintain contact with opponent (unlike gymnastics)
- Controlled entry and exit maintaining combat readiness

Sources:
- CapoeiraWiki movement analysis
- Gymnastics cartwheel biomechanics research
"""

from typing import List
from analyzer.movement_scorer import MovementScorer, AngleCriterion, create_criterion


class AuScorer(MovementScorer):
    """
    Scores the Au (Cartwheel) movement.

    The au is assessed on:
    1. Arm extension - arms straight during support (160-180°)
    2. Leg extension - legs spread and straight at peak (155-180°)
    3. Hip opening - full extension at peak
    4. Controlled landing - return to ready stance

    Based on cartwheel biomechanics and capoeira requirements.
    """

    # ================================================================
    # CALIBRATED VALUES - Based on cartwheel biomechanics
    # Arms must be straight to safely support body weight
    # Legs spread wide and straight at peak for proper form
    # ================================================================

    # Elbow angles during support (degrees)
    # Arms must be straight to support body weight safely
    IDEAL_ELBOW_ANGLE_MIN = 160  # Nearly straight
    IDEAL_ELBOW_ANGLE_MAX = 180  # Full extension

    # Shoulder angles (degrees)
    # Arms overhead during cartwheel
    IDEAL_SHOULDER_ANGLE_MIN = 150  # High overhead
    IDEAL_SHOULDER_ANGLE_MAX = 180  # Full reach

    # Knee angles at peak (degrees)
    # Legs should be straight and spread
    IDEAL_KNEE_ANGLE_MIN = 155  # Nearly straight
    IDEAL_KNEE_ANGLE_MAX = 180  # Full extension

    # Hip angles (degrees)
    # Full hip opening at peak, varied at entry/exit
    IDEAL_HIP_ANGLE_MIN = 120  # Entry/exit phases
    IDEAL_HIP_ANGLE_MAX = 180  # Full extension at peak

    def _setup(self):
        """Set up au-specific scoring criteria."""
        self.movement_name = "Au"
        self.movement_name_pt = "Aú"
        self.description = (
            "The au (cartwheel) is a fundamental capoeira acrobatic used for "
            "evasion and repositioning. Unlike gymnastics cartwheels, the "
            "capoeira au maintains visual contact with the opponent. Arms "
            "must be fully extended to safely support body weight."
        )

        self.criteria = [
            create_criterion(
                name="Left Arm Extension",
                angle_key="left_elbow",
                ideal_min=self.IDEAL_ELBOW_ANGLE_MIN,
                ideal_max=self.IDEAL_ELBOW_ANGLE_MAX,
                weight=1.0,
                description="Arms straight during support (160-180°)"
            ),
            create_criterion(
                name="Right Arm Extension",
                angle_key="right_elbow",
                ideal_min=self.IDEAL_ELBOW_ANGLE_MIN,
                ideal_max=self.IDEAL_ELBOW_ANGLE_MAX,
                weight=1.0,
                description="Arms straight during support (160-180°)"
            ),
            create_criterion(
                name="Left Shoulder Reach",
                angle_key="left_shoulder",
                ideal_min=self.IDEAL_SHOULDER_ANGLE_MIN,
                ideal_max=self.IDEAL_SHOULDER_ANGLE_MAX,
                weight=0.8,
                description="Arms overhead (150-180°)"
            ),
            create_criterion(
                name="Right Shoulder Reach",
                angle_key="right_shoulder",
                ideal_min=self.IDEAL_SHOULDER_ANGLE_MIN,
                ideal_max=self.IDEAL_SHOULDER_ANGLE_MAX,
                weight=0.8,
                description="Arms overhead (150-180°)"
            ),
            create_criterion(
                name="Left Leg Extension",
                angle_key="left_knee",
                ideal_min=self.IDEAL_KNEE_ANGLE_MIN,
                ideal_max=self.IDEAL_KNEE_ANGLE_MAX,
                weight=1.0,
                description="Legs straight at peak (155-180°)"
            ),
            create_criterion(
                name="Right Leg Extension",
                angle_key="right_knee",
                ideal_min=self.IDEAL_KNEE_ANGLE_MIN,
                ideal_max=self.IDEAL_KNEE_ANGLE_MAX,
                weight=1.0,
                description="Legs straight at peak (155-180°)"
            ),
            create_criterion(
                name="Left Hip Opening",
                angle_key="left_hip",
                ideal_min=self.IDEAL_HIP_ANGLE_MIN,
                ideal_max=self.IDEAL_HIP_ANGLE_MAX,
                weight=0.9,
                description="Full hip extension at peak (120-180°)"
            ),
            create_criterion(
                name="Right Hip Opening",
                angle_key="right_hip",
                ideal_min=self.IDEAL_HIP_ANGLE_MIN,
                ideal_max=self.IDEAL_HIP_ANGLE_MAX,
                weight=0.9,
                description="Full hip extension at peak (120-180°)"
            ),
        ]

        self.common_mistakes = [
            "Bent arms during support - risk of collapse (<160°)",
            "Bent legs at peak - should be straight and spread (>155°)",
            "Rushing through without control",
            "Looking at ground instead of opponent",
            "Landing off balance or stumbling",
            "Legs too close together at peak",
            "Body not passing through vertical plane",
            "Hands placed too close together",
            "Not returning to ready stance",
        ]

    def get_calibration_guide(self) -> str:
        """Returns biomechanical reference for au technique."""
        return """
        AU (CARTWHEEL) BIOMECHANICAL REFERENCE
        ======================================

        CALIBRATED VALUES:
        - Elbow angle: 160-180° (arms straight for safety)
        - Shoulder angle: 150-180° (arms overhead)
        - Knee angle: 155-180° (legs straight and spread)
        - Hip angle: 120-180° (full extension at peak)

        FLAWLESS EXECUTION CRITERIA:
        1. Arms fully extended during support phase
        2. Legs spread wide and straight at peak
        3. Body passes through vertical plane
        4. Eyes maintain opponent contact
        5. Controlled landing to ready stance

        CAPOEIRA-SPECIFIC:
        Unlike gymnastics, maintain visual contact with
        opponent throughout the movement.
        """


def create_au_scorer() -> AuScorer:
    """Create and return an AuScorer instance."""
    return AuScorer()
