# regime/classifier.py

import numpy as np
import pandas as pd

from utility.stat_tests import StatTests
from utility.time_series import TimeSeriesStats
from regime.config import RegimeConfig


class RegimeClassifier:
    """
    Regime detection engine (NO trading logic)

    - Walk-forward safe
    - Cached heavy statistics
    - Stateless w.r.t capital
    """

    POSITION_MULTIPLIER = {
        "NORMAL": 1.0,
        "DEGRADED": 0.5,
        "RESET": 0.0,
        "BROKEN": 0.0,
    }

    def __init__(self, config: RegimeConfig | None = None):
        self.config = config or RegimeConfig()

        # cached heavy metrics
        self._adf_p = None
        self._coint_p = None
        self._hurst = None

        self.last_regime = None

    # ====================================================
    # MAIN WALK-FORWARD STEP
    # ====================================================

    def evaluate(
        self,
        t: int,
        x: pd.Series,
        y: pd.Series,
        spread: pd.Series,
    ) -> dict | None:
        """
        Evaluate regime at time t using only data <= t
        """

        W = self.config.MIN_WINDOW
        if t < W:
            return None

        # ------------------------------------------------
        # FIXED WINDOW SLICE
        # ------------------------------------------------
        x_w = x.iloc[t - W : t]
        y_w = y.iloc[t - W : t]
        s_w = spread.iloc[t - W : t]

        # =================================================
        # HEAVY METRICS (CACHED + THROTTLED)
        # =================================================

        # ADF
        if self._adf_p is None or t % self.config.ADF_STEP == 0:
            self._adf_p = StatTests.adf_test(
                s_w.iloc[-self.config.ADF_WINDOW :]
            )["p_value"]

        # COINTEGRATION
        if self._coint_p is None or t % self.config.COINT_STEP == 0:
            self._coint_p = StatTests.cointegration_test(
                x_w.iloc[-self.config.COINT_WINDOW :],
                y_w.iloc[-self.config.COINT_WINDOW :],
            )["p_value"]

        # HURST
        if self._hurst is None or t % self.config.HURST_STEP == 0:
            self._hurst = TimeSeriesStats.hurst_exponent(
                s_w.iloc[-self.config.HURST_WINDOW :]
            )

        # =================================================
        # LIGHT METRICS (DAILY)
        # =================================================

        corr = StatTests.corr(
            x_w.iloc[-self.config.CORR_WINDOW :],
            y_w.iloc[-self.config.CORR_WINDOW :],
        )

        half_life = TimeSeriesStats.half_life(s_w)

        # =================================================
        # SCORES (0–1)
        # =================================================

        structural_score = self._structural_score(
            self._coint_p, self._adf_p
        )

        mr_score = self._mr_score(
            half_life, self._hurst
        )

        coupling_score = np.clip(abs(corr), 0.0, 1.0)
        shock_score = self._shock_score(s_w)

        # =================================================
        # REGIME STATE MACHINE
        # =================================================

        if structural_score < self.config.STRUCT_MIN:
            regime = "BROKEN"

        elif shock_score < self.config.SHOCK_MIN:
            regime = "RESET"

        elif (
            mr_score < self.config.MR_MIN
            or coupling_score < self.config.COUPLING_MIN
        ):
            regime = "DEGRADED"

        else:
            regime = "NORMAL"

        self.last_regime = regime

        # =================================================
        # OUTPUT
        # =================================================

        return {
            "t": t,
            "regime": regime,
            "position_multiplier": self.position_multiplier(regime),
            "scores": {
                "structural": structural_score,
                "mr": mr_score,
                "coupling": coupling_score,
                "shock": shock_score,
            },
            "raw": {
                "adf_p": self._adf_p,
                "coint_p": self._coint_p,
                "hurst": self._hurst,
                "half_life": half_life,
                "corr": corr,
            },
        }

    # ====================================================
    # SCORE HELPERS
    # ====================================================

    @staticmethod
    def _structural_score(coint_p: float, adf_p: float) -> float:
        coint_score = 1.0 - np.clip(coint_p, 0.0, 1.0)
        adf_score = 1.0 - np.clip(adf_p, 0.0, 1.0)
        return 0.5 * coint_score + 0.5 * adf_score

    @staticmethod
    def _mr_score(half_life: float, hurst: float) -> float:
        if half_life <= 0 or np.isinf(half_life):
            return 0.0

        hl_ok = (
            half_life >= 2 and half_life <= 80
        )
        hl_score = 1.0 if hl_ok else np.exp(-half_life / 50.0)

        hurst_score = np.clip(1.0 - hurst, 0.0, 1.0)
        return 0.5 * hl_score + 0.5 * hurst_score

    @staticmethod
    def _shock_score(spread: pd.Series) -> float:
        mu = spread.mean()
        sigma = spread.std()

        if sigma == 0:
            return 0.0

        z = (spread.iloc[-1] - mu) / sigma
        return float(np.exp(-abs(z)))

    # ====================================================
    # POSITION MULTIPLIER
    # ====================================================

    @classmethod
    def position_multiplier(cls, regime: str) -> float:
        return cls.POSITION_MULTIPLIER.get(regime, 0.0)


    # ====================================================
    # WALK-FORWARD ADAPTER
    # ====================================================

    def step(
        self,
        t: int,
        x,
        y,
        spread,
        **_
    ):
        """
        Walk-forward compatible interface
        """
        return self.evaluate(
            t=t,
            x=x,
            y=y,
            spread=spread
        )