# diagnostics/spread_gate.py

class SpreadGate:

    @staticmethod
    def is_tradable(adf_p, half_life, hurst, stab_score,
                    hl_min=5, hl_max=120) -> bool:

        if adf_p > 0.05:
            return False
        if not (hl_min <= half_life <= hl_max):
            return False
        if hurst >= 0.5:
            return False
        if stab_score < 0.6:
            return False

        return True
