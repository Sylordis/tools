from typing import Any, Callable


class DictSelectorHelpers:
    "Contains different selectors to single out data series from dictionaries."

    @staticmethod
    def of_series(
        series_name: str, transformer: Callable[[list], Any] | None = None
    ) -> Callable[[dict], Any]:
        """
        Selects a single series in a dict from its key.

        :param series_name: Name of the series to extract
        :param transformer: transformer to apply to the series. Default is None, e.g. no transformation applied.
        :return: an object, either the series or
        """
        return lambda d: (
            transformer(d[series_name]) if transformer is not None else d[series_name]
        )
