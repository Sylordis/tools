import logging
import pandas as pd
from pathlib import Path
from typing import Any, Callable, TypeAlias

DEFAULT_N_SAMPLES: int = 1000


class DataSeries:
    """
    Defines a series of values (csv column).

    Attributes
    ----------

    name: str = name
        Name of the series.
    generator: Callable[[int,dict], list] = generator
        Callable to generate the series, taking into input a number of samples and varargs.
    formatter: Callable[[Any],Any] = formatter
        Data formatter.
    kwargs
        Arguments for the generator.
    """

    def __init__(
        self,
        name: str,
        generator: Callable[[int, dict], list],
        formatter: Callable[[Any], Any] | None = None,
        **kwargs,
    ):
        """
        Creates a new data series.

        :param name: Name of the series
        :param generator: Callable to generate the series, taking into input a number of samples and varargs
        :param formatter: Data formatter
        :param kwargs: Arguments for the generator
        """
        self.name: str = name
        "Name of the series."
        self.generator: Callable[[int, dict], list] = generator
        "Callable to generate the series, taking into input a number of samples and varargs"
        self.formatter: Callable[[Any], Any] = formatter
        "Data formatter"
        self.kwargs = kwargs
        "Arguments for the generator."

    def generate_data(self, nsamples: int) -> list:
        "Generates N samples of data and formats it if necessary."
        data = self.generator(nsamples, **self.kwargs)
        data_formatted = data
        if self.formatter is not None:
            data_formatted = [self.formatter(d) for d in data]
        return data_formatted


class DataGenerator:
    """
    Generates several series of data.

    :param output: output file for the series of samples
    :param series: all series of data to generate
    :param output_data_transformer: data transformer to apply before exporting.
    """

    def __init__(
        self,
        series: list[DataSeries],
        output_data_transformer: Callable[[dict], dict] | None = None,
        output: Path | None = None,
    ):
        """
        Creates a new Data generator.

        :param output: output file for the series of samples
        :param series: all series of data to generate
        :param output_data_transformer: data transformer to apply before exporting.
        """
        self.series = series
        self.output = output
        self.output_data_transformer = output_data_transformer
        self.generated_data: dict[str, list] = {}

    def generate_series(self, nsamples: int):
        "Generates all series with n samples."
        self.generated_data = {}
        for series in self.series:
            self.generated_data[series.name] = series.generate_data(nsamples)

    def generate_and_export(self, nsamples: int = DEFAULT_N_SAMPLES):
        """
        Generates the series and exports.
        """
        self.generate_series(nsamples)
        self.export()

    def export(self, output_file: Path | None = None):
        """
        Exports the series to the setup output file or a custom one, applying the data transformer before.

        :param output_file: custom file to export the data to
        """
        target = self.output if output_file is None else output_file
        data_transformed = (
            self.generated_data
            if self.output_data_transformer is None
            else self.output_data_transformer(self.generated_data)
        )
        if target is not None:
            pd.DataFrame(data_transformed).to_csv(path_or_buf=None, index=False)
        else:
            with open(target, mode="w", newline="\n") as datafile:
                pd.DataFrame(data_transformed).to_csv(datafile, index=False)


class StatisticsSeries:
    """
    A statistic item to generated, part of a bigger set.

    :param name: name of the statistics series
    :param generator: callable to generate the wanted statistics from a list of samples
    :param formatter: data formatter
    """

    def __init__(
        self,
        name: str,
        generator: Callable[[dict], Any],
        formatter: Callable[[Any], Any] | None = None,
    ):
        """
        Creates a new item.

        :param name: name of the statistics series
        :param generator: callable to generate the wanted statistics from a list of samples
        :param formatter: data formatter, default None.
        """
        self.name = name
        "Name of the statistics series."
        self.generator = generator
        "Callable to generate the wanted statistics from a list of samples."
        self.formatter = formatter
        "Data formatter."

    def generate_statistics(self, data: dict[str, list]):
        "Generates the given statistic."
        stat_data = self.generator(data)
        stat_formatted = stat_data
        if self.formatter is not None:
            stat_formatted = self.formatter(stat_data)
        return stat_formatted


class StatisticsGenerator:
    """
    Instructions to create statistics about a series.

    Attributes
    ----------
    output
      Output file (csv).
    items
      All statistic items to generate.
    generated_data
      Generated data once statistics are generated, empty otherwise.
    """

    def __init__(self, items: list[StatisticsSeries], output: Path | None = None):
        """
        Creates a new statistics series.

        :param output: output file
        :param items: all statistic items to generate
        """
        self.items = items
        self.output = output
        self.generated_data: dict[str, Any] = {}

    def generate_statistics(self, data: dict[str, list]):
        """
        Generates the statistics as a dictionary.
        :param data: list of data to generate statistics on.
        """
        self.generated_data = {}
        for series in self.items:
            self.generated_data[series.name] = series.generate_statistics(data)

    def generate_and_export(self, data: dict[str, list]):
        """
        Generates the statistics values and exports.
        """
        self.generate_statistics(data)
        self.export()

    def export(self, output_file: Path | None = None):
        """
        Exports the statistics series to the setup output file or a custom one, applying the data transformer before.

        :param output_file: custom file to export the data to
        """
        target = self.output if output_file is None else output_file
        header = ",".join([str(item) for item in self.generated_data.keys()])
        data = ",".join([str(item) for item in self.generated_data.values()])
        if target is None:
            print(f"{header}\n")
            print(f"{data}\n")
        else:
            with open(target, mode="w", newline="\n") as statsfile:
                statsfile.write(f"{header}\n")
                statsfile.write(f"{data}\n")


Generator: TypeAlias = DataGenerator | StatisticsGenerator


class GeneratorOverlord:
    """
    Overlord for organising the exports, dispatching each path to a generator in the provided order and
    providing the data generators to the following statistics generators.
    """

    def __init__(self, generators: list[Generator]):
        self.generators = generators
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

    def generate_and_export_all(
        self, targets: list[str], nsamples: int = DEFAULT_N_SAMPLES
    ):
        """
        Generate all series, attributing each target path in order to its list of generators.
        Each statistics generator will be fed the previous data generator's data.

        :param targets: a list of path to files to feed to the generators that will be converted to a list of paths and fed to the generators.
        :param nsamples: amount of sample to generate for each data generator. Default is DEFAULT_N_SAMPLES.
        """
        last_data_generator: DataGenerator | None = None
        if len(targets) != len(self.generators):
            self.logger.warning(
                f"Amount of provided files ({len(targets)}) does not match the amount of generators ({len(self.generators)})."
            )
        for generator, target in zip(self.generators, targets):
            generator.output = Path(target)
            if type(generator) is DataGenerator:
                last_data_generator = generator
                generator.generate_and_export(nsamples)
            elif type(generator) is StatisticsGenerator:
                generator.generate_and_export(last_data_generator.generated_data)
            self.logger.info(f"File created: {target}")
