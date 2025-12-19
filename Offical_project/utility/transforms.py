# utility/transforms.py

import pandas as pd


class Transforms:

    @staticmethod
    def zscore(series: pd.Series, window=60) -> pd.Series:
        mean = series.rolling(window).mean()
        std = series.rolling(window).std()
        return (series - mean) / std
