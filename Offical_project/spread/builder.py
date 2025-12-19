# spread/builder.py

import pandas as pd


class SpreadBuilder:
    """
    Spread construction utilities
    """

    @staticmethod
    def build(
        x: pd.Series,
        y: pd.Series,
        beta
    ) -> pd.Series:
        """
        Spread = x - beta * y

        beta:
            - float (static)
            - pd.Series (rolling)
        """
        return x - beta * y

    @staticmethod
    def normalize(
        spread: pd.Series,
        window: int = 60
    ) -> pd.Series:
        """
        Z-score normalized spread
        """
        mean = spread.rolling(window).mean()
        std = spread.rolling(window).std()
        return (spread - mean) / std
