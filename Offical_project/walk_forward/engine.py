# walk_forward/engine.py

from typing import Dict, List, Any


class WalkForwardEngine:
    """
    Generic walk-forward engine

    - Single timeline loop
    - Module-agnostic
    - Walk-forward safe
    """

    def __init__(
        self,
        data: Dict[str, Any],
        modules: List[Any],
        start_index: int = 0,
    ):
        """
        Parameters
        ----------
        data : dict
            Shared data dictionary.
            Example:
            {
                "x": pd.Series,
                "y": pd.Series,
                "spread": pd.Series,
                "dates": pd.Index
            }

        modules : list
            List of modules implementing:
                step(t, **data, **context) -> dict | None

        start_index : int
            Earliest index to start walk-forward
        """
        self.data = data
        self.modules = modules
        self.start_index = start_index

        # output storage
        self.outputs: Dict[str, list] = {
            module.__class__.__name__: []
            for module in modules
        }

    # ====================================================
    # RUN ENGINE
    # ====================================================

    def run(self) -> Dict[str, List[Any]]:
        """
        Run walk-forward over full timeline
        """

        T = self._infer_length()

        for t in range(self.start_index, T):
            context = {}

            for module in self.modules:
                name = module.__class__.__name__

                out = module.step(
                    t=t,
                    **self.data,
                    **context
                )

                context[name] = out
                self.outputs[name].append(out)

        return self.outputs

    # ====================================================
    # HELPERS
    # ====================================================

    def _infer_length(self) -> int:
        """
        Infer timeline length from data
        """
        for v in self.data.values():
            try:
                return len(v)
            except TypeError:
                continue
        raise ValueError("Cannot infer data length for walk-forward")
