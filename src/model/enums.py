from enum import StrEnum

class RingType(StrEnum):
    """TODO: docstring"""
    TOWER = "tower"
    HAND = "hand"
    BOTH = "both"
    OTHER = "other"

class PerformanceType(StrEnum):
    """TODO: docstring"""
    PEAL = "peal"
    QP = "qp"
    BOTH = "both"
    OTHER = "other"

class Stage(StrEnum):
    """TODO: docstring"""
    SINGLES = "Singles"
    MINIMUS = "Minimus"
    DOUBLES = "Doubles"
    MINOR = "Minor"
    TRIPLES = "Triples"
    MAJOR = "Major"
    CATERS = "Caters"
    ROYAL = "Royal"
    CINQUES = "Cinques"
    MAXIMUS = "Maximus"
    FOURTEEN = "Fourteen"
    SIXTEEN = "Sixteen"
    UNKNOWN = "unknown"

    def get_ordinal(self) -> int:
        """TODO: docstring"""
        stage_ordinals = {
            Stage.SINGLES: 3,
            Stage.MINIMUS: 4,
            Stage.DOUBLES: 5,
            Stage.MINOR: 6,
            Stage.TRIPLES: 7,
            Stage.MAJOR: 8,
            Stage.CATERS: 9,
            Stage.ROYAL: 10,
            Stage.CINQUES: 11,
            Stage.MAXIMUS: 12,
            Stage.FOURTEEN: 14,
            Stage.SIXTEEN: 16,
            Stage.UNKNOWN: None
        }
        return stage_ordinals[self]