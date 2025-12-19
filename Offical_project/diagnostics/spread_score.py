# diagnostics/spread_score.py

from utility.stat_tests import StatTests
from utility.time_series import TimeSeriesStats


class SpreadScore:

    @staticmethod
    def half_life_score(hl: float,
                        hl_min=5,
                        hl_max=60) -> float:
        if hl < hl_min or hl > hl_max:
            return 0.0
        return 1.0

    @staticmethod
    def raw_score(x, y, spread) -> dict:
        corr = abs(StatTests.corr(x, y))

        coint_p = StatTests.cointegration_test(x, y)["p_value"]
        adf_p = StatTests.adf_test(spread)["p_value"]

        hl = TimeSeriesStats.half_life(spread)
        hurst = TimeSeriesStats.hurst_exponent(spread)
        vr = TimeSeriesStats.variance_ratio(spread)

        scores = {
            "corr": corr,
            "coint": 1 - coint_p,
            "adf": 1 - adf_p,
            "half_life": SpreadScore.half_life_score(hl),
            "hurst": max(0, 1 - hurst),
            "vr": max(0, 1 - vr),
        }

        weights = {
            "corr": 0.05,
            "coint": 0.30,
            "adf": 0.25,
            "half_life": 0.20,
            "hurst": 0.10,
            "vr": 0.10,
        }

        total = sum(scores[k] * weights[k] for k in scores)

        return {
            **scores,
            "half_life_raw": hl,
            "hurst_raw": hurst,
            "vr_raw": vr,
            "total_score": total
        }
