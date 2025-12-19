# utility/stat_tests.py

import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint


class StatTests:

    @staticmethod
    def corr(x: pd.Series, y: pd.Series, method="pearson") -> float:
        return x.corr(y, method=method)

    @staticmethod
    def adf_test(series: pd.Series) -> dict:
        result = adfuller(series.dropna(), autolag="AIC")
        return {
            "adf_stat": result[0],
            "p_value": result[1],
            "critical_values": result[4],
            "is_stationary": result[1] < 0.05
        }

    @staticmethod
    def cointegration_test(x: pd.Series, y: pd.Series) -> dict:
        score, p_value, _ = coint(x, y)
        return {
            "coint_stat": score,
            "p_value": p_value,
            "is_coint": p_value < 0.05
        }
