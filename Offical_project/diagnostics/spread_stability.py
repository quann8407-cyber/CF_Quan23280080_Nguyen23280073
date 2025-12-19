# diagnostics/spread_stability.py

import numpy as np
from statsmodels.tsa.stattools import adfuller, coint
from utility.time_series import TimeSeriesStats


class SpreadStability:

    @staticmethod
    def rolling_adf(spread, window=90, step=5):
        flags = []
        for i in range(window, len(spread), step):
            p = adfuller(spread[i-window:i])[1]
            flags.append(p < 0.05)
        return np.mean(flags)

    @staticmethod
    def rolling_coint(x, y, window=180, step=10):
        flags = []
        for i in range(window, len(x), step):
            p = coint(x[i-window:i], y[i-window:i])[1]
            flags.append(p < 0.05)
        return np.mean(flags)

    @staticmethod
    def rolling_half_life(spread, window=60, hl_min=2, hl_max=80):
        flags = []
        for i in range(window, len(spread)):
            hl = TimeSeriesStats.half_life(spread[i-window:i])
            flags.append(hl_min <= hl <= hl_max)
        return np.mean(flags)

    @staticmethod
    def rolling_hurst(spread, window=100, threshold=0.5):
        flags = []
        for i in range(window, len(spread)):
            h = TimeSeriesStats.hurst_exponent(spread[i-window:i])
            flags.append(h < threshold)
        return np.mean(flags)

    @staticmethod
    def stab_score(x, y, spread) -> dict:
        scores = {
            "coint_stab": SpreadStability.rolling_coint(x, y),
            "adf_stab": SpreadStability.rolling_adf(spread),
            "hl_stab": SpreadStability.rolling_half_life(spread),
            "hurst_stab": SpreadStability.rolling_hurst(spread),
        }

        weights = {
            "coint_stab": 0.35,
            "adf_stab": 0.30,
            "hl_stab": 0.20,
            "hurst_stab": 0.15,
        }

        stab = sum(scores[k] * weights[k] for k in scores)

        return {
            **scores,
            "stab_score": stab
        }
