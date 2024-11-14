# This is an example on how to generate data and statistics using the data_generation module.
# Usage: python -m data_generation file1.csv file2.csv

import statistics
import sys
import numpy as np

from .format_helpers import FormatHelpers
from .generators import Generators, SingleGenerators
from .data_transformation_helpers import EntryTransformers, DataTransformationHelpers
from .selectors_helpers import DictSelectorHelpers
from .data_generation import DataSeries, DataGenerator, StatisticsGenerator, StatisticsSeries, GeneratorOverlord


def main() -> int:
    rand = np.random.default_rng()
    serie_x = DataSeries(
        "x", Generators.normal_distribution, FormatHelpers.to_float(2), mu=rand.random()
    )
    generator: DataGenerator = DataGenerator(
        [serie_x],
        lambda d : DataTransformationHelpers.to_histogram(
            d,
            serie_x.name,
            serie_x.name,
            'entries',
            EntryTransformers.to_percentile
        )
    )

    stats: StatisticsGenerator = StatisticsGenerator(
        [
            StatisticsSeries("Minimum", DictSelectorHelpers.of_series(serie_x.name, min)),
            StatisticsSeries("Maximum", DictSelectorHelpers.of_series(serie_x.name, max)),
            StatisticsSeries(
                "Mean",
                DictSelectorHelpers.of_series(serie_x.name, statistics.mean),
                FormatHelpers.to_float(2),
            ),
            StatisticsSeries("MIN_TLA", lambda _: SingleGenerators.random_tla()),
            StatisticsSeries("MAX_TLA", lambda _: SingleGenerators.random_tla()),
            StatisticsSeries(
                "TLA", lambda _: rand.random(), FormatHelpers.to_float(2)
            ),
        ],
    )

    overlord = GeneratorOverlord([generator, stats])
    overlord.generate_and_export_all(sys.argv[1:])
