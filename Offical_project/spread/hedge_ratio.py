# spread/hedge_ratio.py

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class HedgeRatio:
    """
    Hedge ratio estimation utilities
    """

    @staticmethod
    def ols(x: pd.Series, y: pd.Series) -> float:
        """
        Static OLS hedge ratio
        x = beta * y + e
        """
        model = LinearRegression(fit_intercept=False)
        model.fit(y.values.reshape(-1, 1), x.values)
        return float(model.coef_[0])

    @staticmethod
    def rolling_ols(
        x: pd.Series,
        y: pd.Series,
        window: int
    ) -> pd.Series:
        """
        Rolling OLS hedge ratio (walk-forward safe)
        """
        betas = []

        for t in range(len(x)):
            if t < window:
                betas.append(np.nan)
            else:
                beta = HedgeRatio.ols(
                    x.iloc[t - window:t],
                    y.iloc[t - window:t]
                )
                betas.append(beta)

        return pd.Series(betas, index=x.index, name="beta")

    @staticmethod
    def clipped(
        beta: float,
        lower: float = -5.0,
        upper: float = 5.0
    ) -> float:
        """
        Prevent extreme hedge ratios
        """
        return float(np.clip(beta, lower, upper))
