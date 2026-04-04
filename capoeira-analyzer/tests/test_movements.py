"""
Tests for the individual movement scorers.
Now tests that scorers ARE calibrated with real biomechanical values.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from movements import (
    GingaScorer, AuScorer, MeiaLuaScorer, ArmadaScorer, BencaoScorer,
    QueixadaScorer, MarteloScorer, EsquivaScorer, NegativaScorer
)


class TestGingaScorer:
    """Tests for GingaScorer."""

    def test_ginga_scorer_creation(self):
        """Test creating a Ginga scorer."""
        scorer = GingaScorer()
        assert scorer.movement_name == "Ginga"
        assert scorer.movement_name_pt == "Ginga"

    def test_ginga_has_criteria(self):
        """Test that Ginga has scoring criteria defined."""
        scorer = GingaScorer()
        assert len(scorer.criteria) >= 5

    def test_ginga_is_calibrated(self):
        """Test that Ginga criteria ARE calibrated with real values."""
        scorer = GingaScorer()
        # Should be calibrated with biomechanical values
        assert scorer.is_calibrated() is True

    def test_ginga_angle_values(self):
        """Test that Ginga has reasonable angle values."""
        scorer = GingaScorer()
        assert scorer.IDEAL_KNEE_BEND_MIN == 115
        assert scorer.IDEAL_KNEE_BEND_MAX == 165
        assert scorer.IDEAL_SPINE_ANGLE_MIN == 155
        assert scorer.IDEAL_SPINE_ANGLE_MAX == 180

    def test_ginga_common_mistakes(self):
        """Test that common mistakes are defined."""
        scorer = GingaScorer()
        assert len(scorer.common_mistakes) > 0

    def test_ginga_calibration_guide(self):
        """Test calibration guide exists."""
        scorer = GingaScorer()
        guide = scorer.get_calibration_guide()
        assert "GINGA" in guide
        # Now should reference calibrated values
        assert "115" in guide or "165" in guide


class TestAuScorer:
    """Tests for AuScorer."""

    def test_au_scorer_creation(self):
        """Test creating an Au scorer."""
        scorer = AuScorer()
        assert scorer.movement_name == "Au"
        assert "cartwheel" in scorer.description.lower()

    def test_au_has_criteria(self):
        """Test that Au has scoring criteria defined."""
        scorer = AuScorer()
        assert len(scorer.criteria) >= 6

    def test_au_is_calibrated(self):
        """Test that Au criteria ARE calibrated."""
        scorer = AuScorer()
        assert scorer.is_calibrated() is True

    def test_au_angle_values(self):
        """Test that Au has reasonable angle values."""
        scorer = AuScorer()
        # Arms must be straight during cartwheel
        assert scorer.IDEAL_ELBOW_ANGLE_MIN >= 160
        assert scorer.IDEAL_KNEE_ANGLE_MIN >= 155


class TestMeiaLuaScorer:
    """Tests for MeiaLuaScorer."""

    def test_meia_lua_scorer_creation(self):
        """Test creating a Meia-lua scorer."""
        scorer = MeiaLuaScorer()
        assert scorer.movement_name == "Meia-lua de Frente"

    def test_meia_lua_has_criteria(self):
        """Test that Meia-lua has scoring criteria defined."""
        scorer = MeiaLuaScorer()
        assert len(scorer.criteria) > 0

    def test_meia_lua_is_calibrated(self):
        """Test that Meia-lua criteria ARE calibrated."""
        scorer = MeiaLuaScorer()
        assert scorer.is_calibrated() is True


class TestArmadaScorer:
    """Tests for ArmadaScorer."""

    def test_armada_scorer_creation(self):
        """Test creating an Armada scorer."""
        scorer = ArmadaScorer()
        assert scorer.movement_name == "Armada"
        assert "spin" in scorer.description.lower()

    def test_armada_has_criteria(self):
        """Test that Armada has scoring criteria defined."""
        scorer = ArmadaScorer()
        assert len(scorer.criteria) > 0

    def test_armada_is_calibrated(self):
        """Test that Armada criteria ARE calibrated."""
        scorer = ArmadaScorer()
        assert scorer.is_calibrated() is True


class TestBencaoScorer:
    """Tests for BencaoScorer."""

    def test_bencao_scorer_creation(self):
        """Test creating a Bencao scorer."""
        scorer = BencaoScorer()
        assert scorer.movement_name == "Bencao"
        assert "push kick" in scorer.description.lower()

    def test_bencao_has_criteria(self):
        """Test that Bencao has scoring criteria defined."""
        scorer = BencaoScorer()
        assert len(scorer.criteria) > 0

    def test_bencao_is_calibrated(self):
        """Test that Bencao criteria ARE calibrated."""
        scorer = BencaoScorer()
        assert scorer.is_calibrated() is True


class TestQueixadaScorer:
    """Tests for QueixadaScorer."""

    def test_queixada_scorer_creation(self):
        """Test creating a Queixada scorer."""
        scorer = QueixadaScorer()
        assert scorer.movement_name == "Queixada"
        assert "crescent" in scorer.description.lower()

    def test_queixada_is_calibrated(self):
        """Test that Queixada criteria ARE calibrated."""
        scorer = QueixadaScorer()
        assert scorer.is_calibrated() is True


class TestMarteloScorer:
    """Tests for MarteloScorer."""

    def test_martelo_scorer_creation(self):
        """Test creating a Martelo scorer."""
        scorer = MarteloScorer()
        assert scorer.movement_name == "Martelo"
        assert "roundhouse" in scorer.description.lower()

    def test_martelo_is_calibrated(self):
        """Test that Martelo criteria ARE calibrated (based on PMC5571909)."""
        scorer = MarteloScorer()
        assert scorer.is_calibrated() is True

    def test_martelo_has_research_reference(self):
        """Test that Martelo references research."""
        scorer = MarteloScorer()
        guide = scorer.get_calibration_guide()
        assert "PMC5571909" in guide


class TestEsquivaScorer:
    """Tests for EsquivaScorer."""

    def test_esquiva_scorer_creation(self):
        """Test creating an Esquiva scorer."""
        scorer = EsquivaScorer()
        assert scorer.movement_name == "Esquiva"
        assert "dodge" in scorer.description.lower()

    def test_esquiva_is_calibrated(self):
        """Test that Esquiva criteria ARE calibrated."""
        scorer = EsquivaScorer()
        assert scorer.is_calibrated() is True


class TestNegativaScorer:
    """Tests for NegativaScorer."""

    def test_negativa_scorer_creation(self):
        """Test creating a Negativa scorer."""
        scorer = NegativaScorer()
        assert scorer.movement_name == "Negativa"
        assert "ground" in scorer.description.lower()

    def test_negativa_is_calibrated(self):
        """Test that Negativa criteria ARE calibrated."""
        scorer = NegativaScorer()
        assert scorer.is_calibrated() is True


class TestAllMovementScorers:
    """Cross-movement tests for all 9 movements."""

    def test_all_scorers_have_description(self):
        """Test that all scorers have descriptions."""
        scorers = [
            GingaScorer(), AuScorer(), MeiaLuaScorer(),
            ArmadaScorer(), BencaoScorer(), QueixadaScorer(),
            MarteloScorer(), EsquivaScorer(), NegativaScorer()
        ]
        for scorer in scorers:
            assert len(scorer.description) > 20, f"{scorer.movement_name} needs description"

    def test_all_scorers_have_common_mistakes(self):
        """Test that all scorers have common mistakes defined."""
        scorers = [
            GingaScorer(), AuScorer(), MeiaLuaScorer(),
            ArmadaScorer(), BencaoScorer(), QueixadaScorer(),
            MarteloScorer(), EsquivaScorer(), NegativaScorer()
        ]
        for scorer in scorers:
            assert len(scorer.common_mistakes) > 0, f"{scorer.movement_name} needs common mistakes"

    def test_all_scorers_are_calibrated(self):
        """Test that ALL scorers are now calibrated with real values."""
        scorers = [
            GingaScorer(), AuScorer(), MeiaLuaScorer(),
            ArmadaScorer(), BencaoScorer(), QueixadaScorer(),
            MarteloScorer(), EsquivaScorer(), NegativaScorer()
        ]
        for scorer in scorers:
            assert scorer.is_calibrated() is True, f"{scorer.movement_name} should be calibrated"

    def test_all_scorers_repr(self):
        """Test that all scorers have proper string representation."""
        scorers = [
            GingaScorer(), AuScorer(), MeiaLuaScorer(),
            ArmadaScorer(), BencaoScorer(), QueixadaScorer(),
            MarteloScorer(), EsquivaScorer(), NegativaScorer()
        ]
        for scorer in scorers:
            repr_str = repr(scorer)
            assert scorer.movement_name in repr_str or scorer.__class__.__name__ in repr_str

    def test_total_movement_count(self):
        """Test that we have 9 calibrated movements."""
        from movements import AVAILABLE_SCORERS
        assert len(AVAILABLE_SCORERS) == 9
