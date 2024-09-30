# This is an example on how to generate data and statistics using the data_generation module.
# Usage: python data_generation_example.py file1.csv file2.csv

import statistics
import sys

from data_generation import *


def main() -> int:
    serie_x = DataSeries(
        "x", GenerationHelpers.normal_distribution, FormatHelpers.to_float(2), mu=4
    )
    generator: DataGenerator = DataGenerator(
        [serie_x],
        lambda d : DataTransformationHelpers.to_counter(d, serie_x.name, serie_x.name, 'entries')
    )

    stats: StatisticsGenerator = StatisticsGenerator(
        [
            StatisticsSeries("Minimum", DictSelectorHelpers.of_series("x", min)),
            StatisticsSeries("Maximum", DictSelectorHelpers.of_series("x", max)),
            StatisticsSeries(
                "Mean",
                DictSelectorHelpers.of_series("x", statistics.mean),
                FormatHelpers.to_float(2),
            ),
            StatisticsSeries("MIN_TLA", lambda _: SingleGenerators.random_tla()),
            StatisticsSeries("MAX_TLA", lambda _: SingleGenerators.random_tla()),
            StatisticsSeries(
                "TLA", lambda _: RANDOM.random(), FormatHelpers.to_float(2)
            ),
        ],
    )

    overlord = GeneratorOverlord([generator, stats])
    overlord.generate_and_export_all(sys.argv[1:])


if __name__ == "__main__":
    main()
