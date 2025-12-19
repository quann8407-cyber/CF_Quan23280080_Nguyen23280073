# execution/backtest.py

import pandas as pd
import numpy as np
from pathlib import Path


class SpreadBacktest:
    """
    Spread-based execution & PnL logger
    Walk-forward compatible
    """

    def __init__(
        self,
        cost_per_turnover: float = 0.0,
        slippage: float = 0.0,
        output_path: str | None = None,
    ):
        """
        Parameters
        ----------
        cost_per_turnover : float
            Cost per 1.0 change in position

        slippage : float
            Extra proportional cost

        output_path : str | None
            If provided → save csv after run
        """
        self.cost = cost_per_turnover
        self.slippage = slippage
        self.output_path = output_path

        self.prev_position = 0.0
        self.equity = 1.0

        # ---- logger ----
        self.records: list[dict] = []

    # ====================================================
    # WALK-FORWARD STEP
    # ====================================================

    def step(
        self,
        t: int,
        spread: pd.Series,
        ZScoreSignal: dict | None = None,
        **_
    ):
        """
        Execute one step and log result
        """

        if ZScoreSignal is None or t == 0:
            out = self._empty_step(t)
            self.records.append(out)
            return out

        position = ZScoreSignal["position"]

        # ---------------------------------------
        # SPREAD RETURN
        # ---------------------------------------
        spread_ret = spread.iloc[t] - spread.iloc[t - 1]

        # ---------------------------------------
        # TURNOVER & COST
        # ---------------------------------------
        turnover = abs(position - self.prev_position)
        trade_cost = turnover * (self.cost + self.slippage)

        # ---------------------------------------
        # PNL
        # ---------------------------------------
        pnl = self.prev_position * spread_ret - trade_cost
        self.equity *= (1.0 + pnl)

        self.prev_position = position

        out = {
            "t": t,
            "position": position,
            "spread_ret": spread_ret,
            "turnover": turnover,
            "cost": trade_cost,
            "pnl": pnl,
            "equity": self.equity,
        }

        self.records.append(out)
        return out

    # ====================================================
    # FINALIZE (CALLED BY ENGINE)
    # ====================================================

    def finalize(self, index: pd.Index | None = None) -> pd.DataFrame:
        """
        Convert logs to DataFrame and optionally save csv
        """
        df = pd.DataFrame(self.records)

        if index is not None and len(index) == len(df):
            df.index = index

        if self.output_path is not None:
            Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.output_path)

        return df

    # ====================================================
    # HELPERS
    # ====================================================

    def _empty_step(self, t):
        return {
            "t": t,
            "position": 0.0,
            "spread_ret": 0.0,
            "turnover": 0.0,
            "cost": 0.0,
            "pnl": 0.0,
            "equity": self.equity,
        }
