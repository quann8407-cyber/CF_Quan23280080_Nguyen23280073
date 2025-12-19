# regime/config.py
from dataclasses import dataclass

@dataclass
class RegimeConfig:
    MIN_WINDOW: int = 250

    COINT_WINDOW: int = 180
    ADF_WINDOW: int = 90
    HURST_WINDOW: int = 100
    CORR_WINDOW: int = 120

    ADF_STEP: int = 10
    COINT_STEP: int = 25
    HURST_STEP: int = 25

    STRUCT_MIN: float = 0.6
    MR_MIN: float = 0.5
    COUPLING_MIN: float = 0.5
    SHOCK_MIN: float = 0.4

    HL_MIN: int = 2
    HL_MAX: int = 80
