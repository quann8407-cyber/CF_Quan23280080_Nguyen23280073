# performance/rolling_metrics.py

import pandas as pd
import numpy as np


class RollingPerformanceMetrics:
    """
    Rolling / time-series performance metrics
    Read from backtest CSV and export rolling metrics to CSV
    """

    def __init__(
        self,
        csv_path: str,
        output_path: str,
        freq: int = 252,
        equity_col: str = "equity",
        pnl_col: str = "pnl",
        position_col: str = "position",
        regime_col: str = "regime",
        date_col: str = "date",
    ):
        self.csv_path = csv_path
        self.output_path = output_path
        self.freq = freq

        self.equity_col = equity_col
        self.pnl_col = pnl_col
        self.position_col = position_col
        self.regime_col = regime_col
        self.date_col = date_col

        self.df = self._load()

    # ======================================================
    # LOAD
    # ======================================================

    def _load(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path)

        if self.date_col in df:
            df[self.date_col] = pd.to_datetime(df[self.date_col])
            df = df.sort_values(self.date_col)
            df = df.set_index(self.date_col)

        df["returns"] = df[self.equity_col].pct_change().fillna(0.0)
        return df

    # ======================================================
    # ROLLING METRICS
    # ======================================================

    def rolling_sharpe(self, window: int) -> pd.Series:
        r = self.df["returns"]
        mean = r.rolling(window).mean()
        std = r.rolling(window).std()

        sharpe = mean / std * np.sqrt(self.freq)
        return sharpe

    def rolling_volatility(self, window: int) -> pd.Series:
        r = self.df["returns"]
        return r.rolling(window).std() * np.sqrt(self.freq)

    def rolling_drawdown(self) -> pd.Series:
        equity = self.df[self.equity_col]
        peak = equity.cummax()
        return equity / peak - 1.0

    def rolling_turnover(self, window: int) -> pd.Series:
        pos = self.df[self.position_col]
        return pos.diff().abs().rolling(window).sum()

    def rolling_exposure(self, window: int) -> pd.Series:
        pos = self.df[self.position_col]
        return pos.abs().rolling(window).mean()

    # ======================================================
    # REGIME-AWARE ROLLING METRICS
    # ======================================================

    def rolling_regime_exposure(self, window: int) -> pd.Series:
        """
        % of days in NORMAL regime in rolling window
        """
        if self.regime_col not in self.df:
            return pd.Series(index=self.df.index, dtype=float)

        return (
            (self.df[self.regime_col] == "NORMAL")
            .astype(int)
            .rolling(window)
            .mean()
        )

    # ======================================================
    # EXPORT
    # ======================================================

    def run(
        self,
        sharpe_window: int = 60,
        vol_window: int = 60,
        turnover_window: int = 20,
        exposure_window: int = 20,
        regime_window: int = 60,
    ) -> pd.DataFrame:
        """
        Compute rolling metrics and save to CSV
        """

        out = pd.DataFrame(index=self.df.index)

        out["equity"] = self.df[self.equity_col]
        out["returns"] = self.df["returns"]

        out[f"rolling_sharpe_{sharpe_window}"] = self.rolling_sharpe(
            sharpe_window
        )
        out[f"rolling_vol_{vol_window}"] = self.rolling_volatility(
            vol_window
        )
        out["drawdown"] = self.rolling_drawdown()

        out[f"rolling_turnover_{turnover_window}"] = self.rolling_turnover(
            turnover_window
        )
        out[f"rolling_exposure_{exposure_window}"] = self.rolling_exposure(
            exposure_window
        )

        if self.regime_col in self.df:
            out[f"pct_normal_regime_{regime_window}"] = (
                self.rolling_regime_exposure(regime_window)
            )

        out.to_csv(self.output_path)
        return out
