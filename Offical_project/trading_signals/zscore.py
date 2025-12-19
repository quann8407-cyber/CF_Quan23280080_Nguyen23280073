# signal/zscore.py

import pandas as pd
import numpy as np


class ZScoreSignal:
    """
    Z-score based signal
    - Always allow all regimes
    - Position size scaled by regime multiplier
    - Direction determined by sign of z-score
    """

    def __init__(
        self,
        window: int = 20,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
    ):
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z

        self.position = 0  # -1, 0, +1

    # ====================================================
    # WALK-FORWARD STEP
    # ====================================================

    def step(
        self,
        t: int,
        spread: pd.Series,
        RegimeClassifier: dict | None = None,
        **_
    ):
        """
        Generate trading signal at time t
        """

        # -----------------------------------------------
        # NEED HISTORY
        # -----------------------------------------------
        if t < self.window:
            return {
                "signal": 0.0,
                "z": np.nan,
                "position": 0.0,
            }

        # -----------------------------------------------
        # Z-SCORE
        # -----------------------------------------------
        hist = spread.iloc[t - self.window : t]
        mu = hist.mean()
        sigma = hist.std()

        if sigma == 0 or np.isnan(sigma):
            return {
                "signal": 0.0,
                "z": 0.0,
                "position": 0.0,
            }

        z = (spread.iloc[t] - mu) / sigma

        # -----------------------------------------------
        # ENTRY / EXIT (DIRECTION FROM Z)
        # -----------------------------------------------
        if self.position == 0:
            if z > self.entry_z:
                self.position = -1
            elif z < -self.entry_z:
                self.position = 1

        elif self.position == 1 and z > -self.exit_z:
            self.position = 0

        elif self.position == -1 and z < self.exit_z:
            self.position = 0

        # -----------------------------------------------
        # REGIME MULTIPLIER
        # -----------------------------------------------
        multiplier = 1.0
        regime = None

        if RegimeClassifier is not None:
            regime = RegimeClassifier.get("regime", None)
            if regime is not None:
                multiplier = RegimeClassifier["position_multiplier"]

        sized_position = self.position * multiplier

        return {
            "signal": sized_position,
            "z": z,
            "position": sized_position,
            "raw_position": self.position,
            "regime": regime,
            "multiplier": multiplier,
        }
