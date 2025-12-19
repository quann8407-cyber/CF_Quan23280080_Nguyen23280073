# utility/time_series.py

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class TimeSeriesStats:

    @staticmethod
    def half_life(spread: pd.Series) -> float:
        spread = spread.dropna()
        lag = spread.shift(1).dropna()
        ret = spread.diff().dropna()
        lag = lag.loc[ret.index]

        model = LinearRegression().fit(
            lag.values.reshape(-1, 1),
            ret.values
        )

        beta = model.coef_[0]
        if beta >= 0:
            return np.inf

        return -np.log(2) / beta

    @staticmethod
    def hurst_exponent(series: pd.Series, max_lag=20) -> float:
        series = series.dropna()
        lags = range(2, max_lag)
        tau = [
            np.sqrt(series.diff(lag).std())
            for lag in lags
        ]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return poly[0] * 2

    @staticmethod
    def variance_ratio(series: pd.Series, lag=2) -> float:
        series = series.dropna()
        var_1 = series.diff().var(ddof=1)
        var_k = series.diff(lag).var(ddof=1) / lag
        return var_k / var_1
