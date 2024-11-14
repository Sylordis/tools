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
    event_id = DataSeries("event_id", Generators.index)
    event_name = DataSeries("event_id", Generators.index)
    message = DataSeries("event_id", Generators.scalar, value="Lorem ipsum")
    criticality = DataSeries("event_id", Generators.of, population=["Very low", "Low", "Moderate", "High", "Very high"])
    timestamp = DataSeries("event_id", Generators.index)
    generator: DataGenerator = DataGenerator(
        [event_id, event_name, message, criticality, timestamp]
    )

    overlord = GeneratorOverlord([generator])
    overlord.generate_and_export_all(sys.argv[1:])
