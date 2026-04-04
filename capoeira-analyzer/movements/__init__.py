"""
Capoeira Movements Module

Contains scoring criteria for specific capoeira movements with
biomechanically-calibrated angle thresholds.

ATTACKS (Golpes):
- Ginga: The fundamental capoeira movement
- Armada: 360° spinning kick
- Meia-lua de frente: Outside crescent kick
- Bencao: Front push kick
- Queixada: Inside crescent kick
- Martelo: Roundhouse kick

DEFENSES (Defesas):
- Esquiva: Dodge/evasion movements
- Negativa: Ground-level evasion

ACROBATICS (Acrobacias):
- Au: Cartwheel

Calibrated using biomechanical research including:
- PMC5571909: Roundhouse kick biomechanics
- Motion capture analysis studies
- Capoeira pedagogy sources

Azerbaijan Capoeira Federation Project
"""

# Fundamental movement
from .ginga import GingaScorer

# Attacks/Kicks
from .armada import ArmadaScorer
from .meia_lua import MeiaLuaScorer
from .bencao import BencaoScorer
from .queixada import QueixadaScorer
from .martelo import MarteloScorer

# Acrobatics
from .au import AuScorer

# Defenses
from .esquiva import EsquivaScorer
from .negativa import NegativaScorer

__all__ = [
    # Fundamental
    'GingaScorer',
    # Attacks
    'ArmadaScorer',
    'MeiaLuaScorer',
    'BencaoScorer',
    'QueixadaScorer',
    'MarteloScorer',
    # Acrobatics
    'AuScorer',
    # Defenses
    'EsquivaScorer',
    'NegativaScorer',
]

# Movement categories for UI
MOVEMENT_CATEGORIES = {
    'Fundamental': ['GingaScorer'],
    'Kicks': ['ArmadaScorer', 'MeiaLuaScorer', 'BencaoScorer', 'QueixadaScorer', 'MarteloScorer'],
    'Acrobatics': ['AuScorer'],
    'Defenses': ['EsquivaScorer', 'NegativaScorer'],
}

# All available scorers by name
AVAILABLE_SCORERS = {
    'ginga': GingaScorer,
    'armada': ArmadaScorer,
    'meia_lua': MeiaLuaScorer,
    'bencao': BencaoScorer,
    'queixada': QueixadaScorer,
    'martelo': MarteloScorer,
    'au': AuScorer,
    'esquiva': EsquivaScorer,
    'negativa': NegativaScorer,
}
