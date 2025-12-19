# spread/diagnostics.py

import pandas as pd
import numpy as np


class SpreadDiagnostics:
    """
    Diagnostics for constructed spread
    """

    @staticmethod
    def summary(spread: pd.Series) -> dict:
        """
        Basic statistics
        """
        return {
            "mean": spread.mean(),
            "std": spread.std(),
            "skew": spread.skew(),
            "kurt": spread.kurtosis(),
            "zero_crossing_rate": SpreadDiagnostics.zero_crossing_rate(spread),
        }

    @staticmethod
    def zero_crossing_rate(spread: pd.Series) -> float:
        """
        Measure oscillation frequency
        """
        s = spread.dropna()
        return ((s.shift(1) * s) < 0).mean()

    @staticmethod
    def spike_ratio(
        spread: pd.Series,
        z_threshold: float = 3.0
    ) -> float:
        """
        Fraction of extreme moves
        """
        z = (spread - spread.mean()) / spread.std()
        return (abs(z) > z_threshold).mean()
    @staticmethod
    def beta_stability(beta: pd.Series) -> float:
    	"""
    	Measure beta smoothness
    	"""
    	return beta.diff().std()
