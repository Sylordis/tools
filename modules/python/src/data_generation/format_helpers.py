from typing import Callable


class FormatHelpers:
    "Contains different formatters to be used as callables."

    @staticmethod
    def to_float(precision: int) -> Callable[[float], float]:
        return lambda f: float(f"%.{precision}f" % f)
