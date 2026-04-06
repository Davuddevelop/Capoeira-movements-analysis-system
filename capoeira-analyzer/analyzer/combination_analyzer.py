"""
Combination/Sequence Analysis System

This module analyzes how well capoeira movements flow together as a combination.
It evaluates:
- Transition smoothness between movements
- Rhythm and timing consistency
- Movement sequence coherence
- Overall flow quality

A good capoeirista doesn't just execute individual movements well - they combine
them into fluid, rhythmic sequences that create the "jogo" (game) of capoeira.

EVALUATION CRITERIA:
1. Transition Quality (30%): How smoothly one movement flows into the next
2. Rhythm Consistency (25%): Maintaining consistent timing/tempo
3. Sequence Logic (20%): Using movements that naturally connect
4. Recovery Time (15%): Quick, controlled transitions between movements
5. Variety (10%): Using diverse movements appropriately

RESEARCH SOURCES:
- Capoeira movement pedagogy studies
- Dance kinesiology principles
- Martial arts flow state research
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from .movement_detector import DetectedMovement, MovementCategory


class CombinationLevel(Enum):
    """Quality levels for combination analysis."""
    MASTER = "Master Flow"        # 95-100: Seamless, artistic combinations
    EXPERT = "Expert Flow"        # 85-94: Very smooth, few hesitations
    ADVANCED = "Advanced Flow"    # 75-84: Good flow with minor breaks
    INTERMEDIATE = "Intermediate" # 65-74: Decent combinations, some awkwardness
    DEVELOPING = "Developing"     # 50-64: Learning to combine movements
    BEGINNER = "Beginner"         # 35-49: Movements mostly isolated
    NOVICE = "Novice"             # 0-34: Little to no flow


# Natural movement transitions in capoeira
# Higher score = more natural/expected transition
TRANSITION_MATRIX = {
    # From Ginga (the base) - connects to everything
    'ginga': {
        'armada': 0.95, 'meia_lua_de_frente': 0.95, 'bencao': 0.90,
        'queixada': 0.90, 'martelo': 0.85, 'esquiva_lateral': 0.95,
        'esquiva_baixa': 0.90, 'cocorinha': 0.85, 'negativa': 0.80,
        'au': 0.75, 'role': 0.70, 'ponteira': 0.90, 'chapa': 0.85,
        'meia_lua_de_compasso': 0.80, 'rasteira': 0.75, 'gancho': 0.80,
        'rabo_de_arraia': 0.80, 'chibata': 0.85, 'pisao': 0.80,
        'joelhada': 0.85, 'cabecada': 0.70, 'ginga_baixa': 0.90,
    },
    # From kicks - typically return to ginga or defense
    'armada': {
        'ginga': 0.95, 'esquiva_lateral': 0.70, 'negativa': 0.65,
        'meia_lua_de_frente': 0.60, 'au': 0.50, 'role': 0.55,
        'martelo': 0.65, 'queixada': 0.60,
    },
    'meia_lua_de_frente': {
        'ginga': 0.95, 'armada': 0.70, 'queixada': 0.75,
        'esquiva_lateral': 0.65, 'negativa': 0.60, 'au': 0.55,
        'martelo': 0.70,
    },
    'bencao': {
        'ginga': 0.95, 'martelo': 0.70, 'armada': 0.65,
        'esquiva_lateral': 0.60, 'negativa': 0.55, 'ponteira': 0.75,
        'chapa': 0.70,
    },
    'queixada': {
        'ginga': 0.95, 'meia_lua_de_frente': 0.75, 'armada': 0.70,
        'esquiva_lateral': 0.65, 'role': 0.60, 'martelo': 0.70,
    },
    'martelo': {
        'ginga': 0.95, 'bencao': 0.70, 'queixada': 0.65,
        'esquiva_lateral': 0.60, 'armada': 0.55, 'gancho': 0.70,
    },
    'meia_lua_de_compasso': {
        'ginga': 0.90, 'negativa': 0.85, 'role': 0.80,
        'au': 0.75, 'esquiva_baixa': 0.70, 'rabo_de_arraia': 0.85,
    },
    'rabo_de_arraia': {
        'ginga': 0.90, 'negativa': 0.85, 'role': 0.80,
        'au': 0.75, 'meia_lua_de_compasso': 0.85,
    },
    'gancho': {
        'ginga': 0.95, 'martelo': 0.75, 'armada': 0.65,
        'esquiva_lateral': 0.60,
    },
    'ponteira': {
        'ginga': 0.95, 'bencao': 0.80, 'martelo': 0.65,
        'esquiva_lateral': 0.60,
    },
    'chapa': {
        'ginga': 0.95, 'bencao': 0.75, 'negativa': 0.65,
        'esquiva_lateral': 0.60,
    },
    'chibata': {
        'ginga': 0.95, 'martelo': 0.70, 'armada': 0.65,
    },
    'pisao': {
        'ginga': 0.95, 'bencao': 0.70, 'negativa': 0.60,
    },
    'joelhada': {
        'ginga': 0.90, 'cabecada': 0.75, 'cotovelhada': 0.80,
    },
    'cotovelhada': {
        'ginga': 0.90, 'joelhada': 0.75, 'cabecada': 0.70,
    },
    'cabecada': {
        'ginga': 0.85, 'esquiva_baixa': 0.70, 'negativa': 0.65,
    },
    # From defenses - connect to attacks or other defenses
    'esquiva_lateral': {
        'ginga': 0.95, 'armada': 0.85, 'meia_lua_de_frente': 0.80,
        'bencao': 0.75, 'au': 0.70, 'negativa': 0.75, 'role': 0.80,
        'rasteira': 0.85, 'martelo': 0.70, 'queixada': 0.75,
    },
    'esquiva_baixa': {
        'ginga': 0.90, 'negativa': 0.85, 'role': 0.80,
        'meia_lua_de_compasso': 0.75, 'au': 0.65, 'rasteira': 0.80,
        'rabo_de_arraia': 0.75,
    },
    'cocorinha': {
        'ginga': 0.95, 'au': 0.70, 'role': 0.75,
        'negativa': 0.80, 'meia_lua_de_compasso': 0.65,
    },
    'negativa': {
        'ginga': 0.85, 'role': 0.90, 'au': 0.75,
        'meia_lua_de_compasso': 0.85, 'rasteira': 0.90,
        'esquiva_lateral': 0.70, 'tesoura': 0.80, 'rabo_de_arraia': 0.80,
    },
    'role': {
        'ginga': 0.85, 'negativa': 0.90, 'au': 0.80,
        'meia_lua_de_compasso': 0.75, 'esquiva_lateral': 0.70,
        'rasteira': 0.85,
    },
    'resistencia': {
        'ginga': 0.90, 'armada': 0.75, 'bencao': 0.70,
    },
    'ginga_baixa': {
        'ginga': 0.95, 'negativa': 0.85, 'esquiva_baixa': 0.80,
        'meia_lua_de_compasso': 0.75, 'rasteira': 0.80,
    },
    'queda_de_quatro': {
        'ginga': 0.80, 'negativa': 0.85, 'role': 0.80,
        'au': 0.70,
    },
    # From acrobatics
    'au': {
        'ginga': 0.90, 'role': 0.85, 'negativa': 0.80,
        'esquiva_lateral': 0.75, 'armada': 0.60, 'au_batido': 0.70,
        'au_fechado': 0.80,
    },
    'au_batido': {
        'ginga': 0.85, 'role': 0.80, 'negativa': 0.75,
        'au': 0.70, 'esquiva_lateral': 0.65,
    },
    'au_fechado': {
        'ginga': 0.85, 'role': 0.80, 'negativa': 0.75,
        'au': 0.80,
    },
    'au_sem_mao': {
        'ginga': 0.85, 'role': 0.75, 'negativa': 0.70,
    },
    'bananeira': {
        'au': 0.85, 'queda_de_rins': 0.75, 'ginga': 0.70,
        'negativa': 0.65, 'piao_de_mao': 0.70,
    },
    'macaco': {
        'ginga': 0.80, 'negativa': 0.75, 'role': 0.70,
        'esquiva_baixa': 0.65, 's_dobrado': 0.60,
    },
    'ponte': {
        'ginga': 0.70, 'negativa': 0.65, 'macaco': 0.75,
    },
    'queda_de_rins': {
        'ginga': 0.75, 'negativa': 0.80, 'bananeira': 0.70,
        'piao_de_mao': 0.75,
    },
    's_dobrado': {
        'ginga': 0.75, 'role': 0.70, 'negativa': 0.65,
    },
    'parafuso': {
        'ginga': 0.80, 'role': 0.70, 'negativa': 0.65,
    },
    'piao_de_mao': {
        'ginga': 0.75, 'bananeira': 0.70, 'queda_de_rins': 0.70,
    },
    'mortal': {
        'ginga': 0.80, 'role': 0.70, 'negativa': 0.60,
    },
    'folha_seca': {
        'ginga': 0.80, 'role': 0.70,
    },
    # From takedowns
    'rasteira': {
        'ginga': 0.85, 'negativa': 0.90, 'role': 0.85,
        'esquiva_lateral': 0.75, 'au': 0.60,
    },
    'banda': {
        'ginga': 0.90, 'esquiva_lateral': 0.70, 'negativa': 0.65,
    },
    'tesoura': {
        'ginga': 0.80, 'negativa': 0.85, 'role': 0.80,
    },
    'vingativa': {
        'ginga': 0.85, 'negativa': 0.75, 'role': 0.70,
    },
}


@dataclass
class TransitionAnalysis:
    """Analysis of a single transition between movements."""
    from_movement: str
    to_movement: str
    quality_score: float  # 0-100
    is_natural: bool
    recovery_time_frames: int
    notes: str = ""


@dataclass
class CombinationResult:
    """Result of combination/sequence analysis."""
    overall_score: float  # 0-100
    level: CombinationLevel

    # Component scores
    transition_score: float
    rhythm_score: float
    sequence_logic_score: float
    recovery_score: float
    variety_score: float

    # Details
    total_movements: int
    unique_movements: int
    transitions_analyzed: int
    smooth_transitions: int

    # Movement sequence
    movement_sequence: List[str]
    transition_details: List[TransitionAnalysis]

    # Feedback
    feedback: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    areas_to_improve: List[str] = field(default_factory=list)


class CombinationAnalyzer:
    """
    Analyzes the quality of movement combinations and sequences.

    Evaluates how well movements flow together, not just individual execution.
    """

    # Weights for final score
    WEIGHT_TRANSITION = 0.30
    WEIGHT_RHYTHM = 0.25
    WEIGHT_SEQUENCE = 0.20
    WEIGHT_RECOVERY = 0.15
    WEIGHT_VARIETY = 0.10

    def __init__(self, fps: float = 30.0):
        """
        Initialize the combination analyzer.

        Args:
            fps: Video frames per second (for timing calculations)
        """
        self.fps = fps
        self.transition_matrix = TRANSITION_MATRIX

    def analyze(self, detections: List[DetectedMovement],
                timestamps: List[float] = None) -> CombinationResult:
        """
        Analyze a sequence of detected movements.

        Args:
            detections: List of detected movements for each frame
            timestamps: Optional list of timestamps for each detection

        Returns:
            CombinationResult with comprehensive analysis
        """
        if not detections:
            return self._empty_result()

        # Filter to valid detections
        valid_detections = [d for d in detections if d is not None and d.confidence >= 0.3]

        if len(valid_detections) < 2:
            return self._empty_result()

        # Extract movement sequence (consolidate consecutive same movements)
        movement_sequence, segment_lengths = self._extract_sequence(valid_detections)

        if len(movement_sequence) < 2:
            return self._single_movement_result(movement_sequence)

        # Analyze transitions
        transitions = self._analyze_transitions(movement_sequence, segment_lengths)

        # Calculate component scores
        transition_score = self._calculate_transition_score(transitions)
        rhythm_score = self._calculate_rhythm_score(segment_lengths)
        sequence_score = self._calculate_sequence_logic_score(movement_sequence)
        recovery_score = self._calculate_recovery_score(transitions, segment_lengths)
        variety_score = self._calculate_variety_score(movement_sequence, valid_detections)

        # Calculate overall score
        overall_score = (
            transition_score * self.WEIGHT_TRANSITION +
            rhythm_score * self.WEIGHT_RHYTHM +
            sequence_score * self.WEIGHT_SEQUENCE +
            recovery_score * self.WEIGHT_RECOVERY +
            variety_score * self.WEIGHT_VARIETY
        )

        # Determine level
        level = self._get_level(overall_score)

        # Generate feedback
        feedback, strengths, improvements = self._generate_feedback(
            transition_score, rhythm_score, sequence_score,
            recovery_score, variety_score, transitions, movement_sequence
        )

        smooth_transitions = sum(1 for t in transitions if t.quality_score >= 70)

        return CombinationResult(
            overall_score=overall_score,
            level=level,
            transition_score=transition_score,
            rhythm_score=rhythm_score,
            sequence_logic_score=sequence_score,
            recovery_score=recovery_score,
            variety_score=variety_score,
            total_movements=len(valid_detections),
            unique_movements=len(set(movement_sequence)),
            transitions_analyzed=len(transitions),
            smooth_transitions=smooth_transitions,
            movement_sequence=movement_sequence,
            transition_details=transitions,
            feedback=feedback,
            strengths=strengths,
            areas_to_improve=improvements
        )

    def _extract_sequence(self, detections: List[DetectedMovement]) -> Tuple[List[str], List[int]]:
        """
        Extract movement sequence by consolidating consecutive same movements.

        Uses a minimum segment duration filter to avoid noise while keeping
        real quick movements like kicks (which can be as short as 3-5 frames).
        """
        if not detections:
            return [], []

        # First pass: extract raw segments
        raw_sequence = []
        raw_lengths = []

        current_movement = detections[0].movement_name
        current_length = 1

        for det in detections[1:]:
            if det.movement_name == current_movement:
                current_length += 1
            else:
                raw_sequence.append(current_movement)
                raw_lengths.append(current_length)
                current_movement = det.movement_name
                current_length = 1

        # Add last segment
        raw_sequence.append(current_movement)
        raw_lengths.append(current_length)

        # Second pass: filter out very short noise segments
        # but keep movements that are naturally quick (kicks)
        # LOWERED thresholds to catch more movements
        MIN_FRAMES_KICK = 2  # Kicks can be very fast (2 frames minimum)
        MIN_FRAMES_OTHER = 3  # Other movements need at least 3 frames

        QUICK_MOVEMENTS = {
            'armada', 'meia_lua_de_frente', 'bencao', 'queixada', 'martelo',
            'ponteira', 'chapa', 'gancho', 'meia_lua_de_compasso', 'chibata',
            'pisao', 'rabo_de_arraia', 'joelhada', 'cotovelhada', 'cabecada',
            'parafuso'
        }

        sequence = []
        segment_lengths = []

        for i, (movement, length) in enumerate(zip(raw_sequence, raw_lengths)):
            min_frames = MIN_FRAMES_KICK if movement in QUICK_MOVEMENTS else MIN_FRAMES_OTHER

            # Keep segment if it meets minimum duration
            if length >= min_frames:
                sequence.append(movement)
                segment_lengths.append(length)
            # Also keep SHORT segments if they're DIFFERENT from neighbors
            # This catches quick kicks/transitions that only last 1-2 frames
            elif length >= 1:
                prev_move = raw_sequence[i-1] if i > 0 else None
                next_move = raw_sequence[i+1] if i < len(raw_sequence)-1 else None
                # Keep if it's a different movement from at least one neighbor
                # This is more permissive - catches real quick movements
                is_different = (prev_move != movement) or (next_move != movement)
                if is_different and movement in QUICK_MOVEMENTS:
                    sequence.append(movement)
                    segment_lengths.append(length)

        # If we filtered everything, return the dominant movement
        if not sequence and raw_sequence:
            # Return the longest segment
            max_idx = raw_lengths.index(max(raw_lengths))
            return [raw_sequence[max_idx]], [raw_lengths[max_idx]]

        return sequence, segment_lengths

    def _analyze_transitions(self, sequence: List[str],
                            segment_lengths: List[int]) -> List[TransitionAnalysis]:
        """Analyze each transition in the sequence."""
        transitions = []

        for i in range(len(sequence) - 1):
            from_move = sequence[i]
            to_move = sequence[i + 1]

            # Get transition quality from matrix
            from_transitions = self.transition_matrix.get(from_move, {})
            quality = from_transitions.get(to_move, 0.5)  # Default 50% if not defined

            # Adjust for recovery time (frames held in previous movement)
            recovery_frames = segment_lengths[i]

            # Very short segments might indicate unstable detection
            if recovery_frames < 3:
                quality *= 0.8  # Penalize very quick transitions

            is_natural = quality >= 0.7

            notes = ""
            if quality >= 0.9:
                notes = "Excellent natural flow"
            elif quality >= 0.7:
                notes = "Good transition"
            elif quality >= 0.5:
                notes = "Acceptable but could be smoother"
            else:
                notes = "Uncommon transition - consider alternatives"

            transitions.append(TransitionAnalysis(
                from_movement=from_move,
                to_movement=to_move,
                quality_score=quality * 100,
                is_natural=is_natural,
                recovery_time_frames=recovery_frames,
                notes=notes
            ))

        return transitions

    def _calculate_transition_score(self, transitions: List[TransitionAnalysis]) -> float:
        """Calculate overall transition quality score."""
        if not transitions:
            return 50.0

        scores = [t.quality_score for t in transitions]
        return np.mean(scores)

    def _calculate_rhythm_score(self, segment_lengths: List[int]) -> float:
        """Calculate rhythm consistency score based on timing."""
        if len(segment_lengths) < 2:
            return 50.0

        # Calculate coefficient of variation (lower = more consistent)
        mean_length = np.mean(segment_lengths)
        std_length = np.std(segment_lengths)

        if mean_length == 0:
            return 50.0

        cv = std_length / mean_length

        # Convert to score (lower CV = higher score)
        # CV of 0 = 100, CV of 1 = 50, CV of 2+ = low scores
        score = max(0, 100 - (cv * 50))

        # Bonus for appropriate movement duration
        # Typical movement should last 0.5-2 seconds at 30fps = 15-60 frames
        appropriate_durations = sum(1 for l in segment_lengths if 10 <= l <= 90)
        duration_bonus = (appropriate_durations / len(segment_lengths)) * 20

        return min(100, score + duration_bonus)

    def _calculate_sequence_logic_score(self, sequence: List[str]) -> float:
        """Calculate how logically the movements connect."""
        if len(sequence) < 2:
            return 50.0

        # Check for patterns that make capoeira sense
        score = 70.0  # Base score

        # Bonus: Returns to ginga (the base)
        ginga_returns = sum(1 for i, m in enumerate(sequence)
                          if m == 'ginga' and i > 0)
        if ginga_returns > 0:
            score += min(15, ginga_returns * 5)

        # Bonus: Attack-defense patterns
        kicks = {'armada', 'meia_lua_de_frente', 'bencao', 'queixada',
                'martelo', 'ponteira', 'chapa', 'meia_lua_de_compasso'}
        defenses = {'esquiva_lateral', 'esquiva_baixa', 'cocorinha',
                   'negativa', 'role'}

        for i in range(len(sequence) - 1):
            if sequence[i] in kicks and sequence[i+1] in defenses:
                score += 3  # Natural attack-to-defense
            elif sequence[i] in defenses and sequence[i+1] in kicks:
                score += 3  # Natural defense-to-attack

        # Penalty: Same category repeated too much
        for i in range(len(sequence) - 2):
            if (sequence[i] in kicks and sequence[i+1] in kicks and
                sequence[i+2] in kicks):
                score -= 5  # Too many kicks in a row

        return min(100, max(0, score))

    def _calculate_recovery_score(self, transitions: List[TransitionAnalysis],
                                  segment_lengths: List[int]) -> float:
        """Calculate recovery/control score."""
        if not transitions:
            return 50.0

        scores = []

        for i, t in enumerate(transitions):
            # Check if recovery time is appropriate
            recovery = segment_lengths[i]

            # Optimal recovery: 15-45 frames (0.5-1.5 sec at 30fps)
            if 15 <= recovery <= 45:
                scores.append(100)
            elif 10 <= recovery <= 60:
                scores.append(80)
            elif 5 <= recovery <= 90:
                scores.append(60)
            else:
                scores.append(40)

            # Bonus for natural transitions with good recovery
            if t.is_natural:
                scores[-1] = min(100, scores[-1] + 10)

        return np.mean(scores)

    def _calculate_variety_score(self, sequence: List[str],
                                 detections: List[DetectedMovement]) -> float:
        """Calculate movement variety score."""
        if not sequence:
            return 50.0

        unique = len(set(sequence))
        total = len(sequence)

        # Variety ratio
        variety_ratio = unique / total if total > 0 else 0

        # Check category diversity
        categories = set()
        for det in detections:
            if det and det.category:
                categories.add(det.category)

        category_bonus = len(categories) * 10

        # Base score from variety ratio (40-70 range)
        base_score = 40 + (variety_ratio * 30)

        # Add category bonus (up to 30 more)
        score = min(100, base_score + category_bonus)

        return score

    def _get_level(self, score: float) -> CombinationLevel:
        """Determine combination level from score."""
        if score >= 95:
            return CombinationLevel.MASTER
        elif score >= 85:
            return CombinationLevel.EXPERT
        elif score >= 75:
            return CombinationLevel.ADVANCED
        elif score >= 65:
            return CombinationLevel.INTERMEDIATE
        elif score >= 50:
            return CombinationLevel.DEVELOPING
        elif score >= 35:
            return CombinationLevel.BEGINNER
        else:
            return CombinationLevel.NOVICE

    def _generate_feedback(self, transition_score, rhythm_score, sequence_score,
                          recovery_score, variety_score, transitions,
                          sequence) -> Tuple[List[str], List[str], List[str]]:
        """Generate feedback based on analysis."""
        feedback = []
        strengths = []
        improvements = []

        # Transition feedback
        if transition_score >= 80:
            strengths.append("Excellent movement transitions - very fluid")
        elif transition_score >= 60:
            feedback.append("Good transitions overall")
        else:
            improvements.append("Work on smoother transitions between movements")

        # Rhythm feedback
        if rhythm_score >= 80:
            strengths.append("Consistent rhythm and timing")
        elif rhythm_score < 60:
            improvements.append("Try to maintain more consistent timing between movements")

        # Sequence logic feedback
        if sequence_score >= 80:
            strengths.append("Logical movement sequences that flow naturally")
        elif sequence_score < 60:
            improvements.append("Practice natural movement combinations (attack-defense patterns)")

        # Recovery feedback
        if recovery_score >= 80:
            strengths.append("Good control and recovery between movements")
        elif recovery_score < 60:
            improvements.append("Focus on controlled transitions - not too rushed or slow")

        # Variety feedback
        if variety_score >= 80:
            strengths.append("Good variety of movements")
        elif variety_score < 50:
            improvements.append("Try incorporating more diverse movements")

        # Specific transition feedback
        poor_transitions = [t for t in transitions if t.quality_score < 50]
        if poor_transitions:
            for t in poor_transitions[:2]:  # Limit to 2
                feedback.append(
                    f"Consider alternative after {t.from_movement} instead of {t.to_movement}"
                )

        # Overall summary
        if len(strengths) >= 3:
            feedback.insert(0, "Strong overall combination skills!")
        elif len(improvements) >= 3:
            feedback.insert(0, "Keep practicing - combinations will become more natural")

        return feedback, strengths, improvements

    def _empty_result(self) -> CombinationResult:
        """Return empty result for insufficient data."""
        return CombinationResult(
            overall_score=0,
            level=CombinationLevel.NOVICE,
            transition_score=0,
            rhythm_score=0,
            sequence_logic_score=0,
            recovery_score=0,
            variety_score=0,
            total_movements=0,
            unique_movements=0,
            transitions_analyzed=0,
            smooth_transitions=0,
            movement_sequence=[],
            transition_details=[],
            feedback=["Not enough movements detected for combination analysis"],
            strengths=[],
            areas_to_improve=[]
        )

    def _single_movement_result(self, sequence: List[str]) -> CombinationResult:
        """Return result for single movement detected."""
        return CombinationResult(
            overall_score=50,
            level=CombinationLevel.DEVELOPING,
            transition_score=50,
            rhythm_score=50,
            sequence_logic_score=50,
            recovery_score=50,
            variety_score=30,
            total_movements=1,
            unique_movements=1,
            transitions_analyzed=0,
            smooth_transitions=0,
            movement_sequence=sequence,
            transition_details=[],
            feedback=["Only one movement type detected - try combining multiple movements"],
            strengths=[],
            areas_to_improve=["Practice combining movements together"]
        )


def analyze_combination(detections: List[DetectedMovement],
                       fps: float = 30.0) -> CombinationResult:
    """
    Convenience function to analyze movement combinations.

    Args:
        detections: List of detected movements
        fps: Video frame rate

    Returns:
        CombinationResult with analysis
    """
    analyzer = CombinationAnalyzer(fps=fps)
    return analyzer.analyze(detections)
