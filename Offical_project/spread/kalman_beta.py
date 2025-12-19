# spread/kalman_beta.py

import numpy as np
import pandas as pd


class KalmanBeta:
    """
    Kalman Filter for time-varying hedge ratio
    """

    def __init__(
        self,
        q: float = 1e-5,   # process noise
        r: float = 1e-3,   # observation noise
        init_beta: float = 1.0,
        init_var: float = 1.0,
        clip: tuple = (-5.0, 5.0)
    ):
        self.q = q
        self.r = r
        self.clip = clip

        self.beta = init_beta
        self.P = init_var

    def update(self, x_t: float, y_t: float) -> float:
        """
        One-step Kalman update
        """
        # ---------- Predict ----------
        beta_pred = self.beta
        P_pred = self.P + self.q

        # ---------- Update ----------
        H = y_t
        innovation = x_t - H * beta_pred
        S = H * P_pred * H + self.r
        K = P_pred * H / S

        self.beta = beta_pred + K * innovation
        self.P = (1 - K * H) * P_pred

        # ---------- Clip ----------
        self.beta = float(np.clip(self.beta, *self.clip))

        return self.beta

    def run(
        self,
        x: pd.Series,
        y: pd.Series
    ) -> pd.Series:
        """
        Walk-forward Kalman beta series
        """
        betas = []

        for t in range(len(x)):
            if np.isnan(x.iloc[t]) or np.isnan(y.iloc[t]):
                betas.append(np.nan)
                continue

            beta_t = self.update(x.iloc[t], y.iloc[t])
            betas.append(beta_t)

        return pd.Series(betas, index=x.index, name="beta_kalman")
