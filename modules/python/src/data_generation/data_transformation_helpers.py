from collections import Counter
from typing import Any, Callable


class EntryTransformers:

    @staticmethod
    def to_percentile(entries: list, value: int | float) -> float:
        """
        Converts a value to a percentage of its value among the sum of all values in a list.

        :param entries: original list of entries
        :param value: value to transform
        :return: a percentage value
        """
        return float(value) * 100 / len(entries)


class DataTransformationHelpers:
    "Contains methods to transform dictionary content and nature."

    @staticmethod
    def to_histogram(
        data: dict[str, list],
        sum_index: str,
        key_index: str,
        values_index: str,
        entry_transformer: Callable[[list, Any], Any] | None = None,
    ) -> dict[str, list]:
        """
        Transforms a given series from a dictionary into a counted occurrence of each value of this series, creating
        2 series with corresponding value => count.

        :param data: original dataframe
        :param sum_index: index of the dataframe to perform a counter of
        :param key_index: index of the resulting dictionary's keys
        :param values_index: index of the resulting dictionary's values
        :param entry_transformer: an optional transformer to pass the generated values through, taking as input the original extracted list
        :return: a dataframe
        """
        counter = Counter(data[sum_index])
        result: dict[str, list] = {key_index: [], values_index: []}
        for k, v in sorted(counter.items()):
            result[key_index].append(k)
            if entry_transformer is None:
                result[values_index].append(v)
            else:
                result[values_index].append(entry_transformer(data[sum_index], v))
        return result
