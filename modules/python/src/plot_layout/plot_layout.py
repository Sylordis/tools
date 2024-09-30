from __future__ import annotations

from dataclasses import dataclass
import math
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
from typing import Callable

from plot import Plot
from plot_configuration import Orientation

DEFAULT_PLOT_WIDTH: float = 3.8
"Default graphical width for one plot or each subplot, in inches."
DEFAULT_PLOT_HEIGHT: float = 4.8
"Default graphical height for one plot or each subplot, in inches."
REASONABLE_SIZE_PER_LINE: int = 4
"""
Reasonable minimum size (amount of plots) on the major layout axis before having to add a new line.

The reasonable size on the minor line is considered as inferior to this one, according to the expansion policy.
"""
MAJOR_TO_MINOR_DIVISOR = 2
"Default divisor for major to minor line size."


@dataclass
class LayoutExpansionPolicy:
    """
    Internal logic related to the expansion policy of a plot with subplots when they are expanding horizontally or vertically.

    It considers a major axis and minor axis, respectively the expansion axis and the other one. The major axis is based on a
    minimum size for which there's no need to add new lines but once this number is passed, the number of subplots should be
    able to fit in a grid of (major size x minor size).

    Attributes
    ----------
    reasonable_minimum_major_size: int
      Reasonable minimum amount of plots on the major axis before considering changing.
    minor_size_provider: Callable[[int],int]
      Provider for the minor axis size, usually related to the major axis size.
    title: str | None
      Title of the policy, strictly for debugging and tests purposes. Default is None.
    """

    reasonable_minimum_major_size: int
    "Reasonable minimum amount of plots on the major axis before considering changing."
    minor_size_provider: Callable[[int], int]
    "Provider for the minor axis size, usually related to the major axis size."
    title: str | None = None
    "Title of the policy, strictly for debugging and tests purposes."

    def __str__(self):
        return f"{self.title}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title})"

    @staticmethod
    def minus(minimum: int, subtrahend: int) -> LayoutExpansionPolicy:
        """
        Expansion policy with which the major axis size is decreased by a certain amount to calculate the minor axis size (with a minimum of 1).

        In more technical: `m = max(1, M - subtrahend)` with: M = major size, m = minor size.

        :param minimum: minimum major size
        :param subtrahend: amount subtracted from the current major size to determine the minor size
        :return: an expansion policy
        """
        return LayoutExpansionPolicy(minimum, lambda n: max(1, n - subtrahend), title=f"M{minimum} & R-{subtrahend}")

    @staticmethod
    def divided_ceil(minimum: int, divisor: int) -> LayoutExpansionPolicy:
        """
        Expansion policy with which the major axis size is divided by a certain amount to calculate the minor axis size (with a minimum of 1).

        In more technical: `m = ceil(M / divisor)` with: M = major size, m = minor size.

        :param minimum: minimum major size
        :param divisor: divisor of the major size to calculate the minor size
        :return: an expansion policy
        """
        return LayoutExpansionPolicy(minimum, lambda n: math.ceil(n / divisor), title=f"M{minimum} & R/{divisor}")


DEFAULT_EXPANSION_POLICY = LayoutExpansionPolicy.divided_ceil(REASONABLE_SIZE_PER_LINE, MAJOR_TO_MINOR_DIVISOR)
"""
Default expansion policy. After multiple experimentations, it seems the most pleasing.

Feel free to redefine one you or the client finds most pleasing for your own plots if you disagree.
"""


@dataclass
class PlotLayoutConfiguration:
    """
    Defines the configuration for a PlotLayout.

    Attributes
    ----------
    orientation: Orientation
      Orientation of the layout, i.e. from which directions the plots are filled in first. Default is Square.
    expansion_policy: LayoutExpansionPolicy | None
      Expansion policy in case the layout has another orientation than the square one. Default is None.
      If left as default (None), the DEFAULT_EXPANSION_POLICY will be used.
    title: str | None
      Overall title of the figure. Default is None, e.g. no title to be added.
    grid : tuple[int,int] | None
      Grid configuration with (nrows, ncols). Setting this attribute overrides the automated grid management done, determined by the orientation
      and the expansion policy, otherwise leave None.
    legend: str | None
      Legend position if it has to be added. Value of the string should be one of the values described on
      https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html. Default is None.
      Don't forget to give different series a label for it to work.
    axis_labels: tuple[str,str] | None
      Common labels for axes, respectively x and y.
    """

    orientation: Orientation = Orientation.SQUARE
    "Orientation of the layout, i.e. from which directions the plots are filled in first. Default is Square."
    expansion_policy: LayoutExpansionPolicy | None = None
    """
    Expansion policy in case the layout has another orientation than the square one.
    If left as default (None), the DEFAULT_EXPANSION_POLICY will be used.
    """
    title: str | None = None
    "Overall title of the plot."
    grid: tuple[int, int] | None = None
    "Grid configuration with (nrows, ncols). Will override the automated grid management done, otherwise leave None."
    legend: str | None = None
    """
    Legend position if it has to be added. Value of the string should be one of the values described on
    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html.
    Don't forget to give different series a label for it to work.
    """
    axis_labels: tuple[str, str] = (None, None)
    "Common labels for axes, respectively x and y."

    def apply_to_figure(self, figure: Figure):
        """
        Applies the configuration to the provided figure.
        """
        if self.title is not None:
            figure.suptitle(self.title)
        if self.legend is not None:
            figure.legend(loc=self.legend)
        x_label, y_label = self.axis_labels
        if x_label is not None:
            figure.supxlabel(x_label)
        if y_label is not None:
            figure.supylabel(y_label)


class PlotLayout:
    """
    Manages a plot with multiple subplots to display them in a layout. Use this class ONLY if you have a plot with subplots.

    Attributes
    ----------
    configuration : PlotLayoutConfiguration
      Configuration of the overall layout. It doesn't define each subplot. Default is empty configuration.
    plots : list[Plot]
      List of plots to consider for this layout. Default is empty list.
    output_path : Path
      Output path for the plot.
    """

    def __init__(
        self,
        plots: list[Plot] | None = None,
        output_path: Path | None = None,
        configuration: PlotLayoutConfiguration | None = None,
    ):
        self.configuration = configuration if configuration is not None else PlotLayoutConfiguration()
        "Configuration of the overall layout. It doesn't define each subplot."
        self.plots = plots if plots is not None else []
        "List of plots to consider for this layout."
        self.output_path = output_path
        "Output path for the plot."

    def get_grid(self) -> tuple[int, int]:
        """
        Calculates or retrieves the grid (number of rows and columns) if specified.

        :return: a tuple with (#rows,#columns)
        """
        value = self.configuration.grid
        if value is None:
            value = self.__auto_grid()
        elif value[0] * value[1] < len(self.plots):
            raise ValueError("The specified grid size is too small for the amount of subplots.")
        return value

    def __auto_grid(self) -> tuple[int, int]:
        """
        Calculates the grid (number of rows and columns) based on the current orientation, the number of plots and the expansion policy (if applicable).

        :return: a tuple (nrows,ncols)
        """
        result: tuple[int, int]
        match self.configuration.orientation:
            case Orientation.X_AXIS | Orientation.Y_AXIS:
                policy = (
                    DEFAULT_EXPANSION_POLICY
                    if self.configuration.expansion_policy is None
                    else self.configuration.expansion_policy
                )
                result = self.__auto_grid_with_policy(policy)
            case _:
                # SQUARE policy
                middle = math.sqrt(len(self.plots))
                ncols = math.ceil(middle)
                nrows = len(self.plots) // ncols
                if ncols * nrows < len(self.plots):
                    nrows += 1
                result = (nrows, ncols)
        return result

    def __auto_grid_with_policy(self, policy: LayoutExpansionPolicy) -> tuple[int, int]:
        """
        Calculates the auto grid in case there's a specific axis expansion according to the expansion policy.

        :param policy: the expansion policy to use
        :return: a tuple (nrows,ncols)
        """
        n_major_size: int
        n_secondary_size: int
        if len(self.plots) <= policy.reasonable_minimum_major_size:
            # If under the minimum major size, just take the amount of plots
            n_major_size = len(self.plots)
            n_secondary_size = 1
        else:
            # Start with the minimum
            n_major_size = policy.reasonable_minimum_major_size
            # Check if the current policy with the current major * calculated minor (acc. to policy) can contain all plots
            while n_major_size * policy.minor_size_provider(n_major_size) < len(self.plots):
                # If not increase major by one
                n_major_size += 1
            # Secondary is the rounded up amount of plots divided by the major size
            n_secondary_size = math.ceil(len(self.plots) / n_major_size)
        # Horizontal/X expands on the number of columns, not rows, and Vertical/Y vice-versa.
        if self.configuration.orientation == Orientation.X_AXIS:
            result = (n_secondary_size, n_major_size)
        else:
            result = (n_major_size, n_secondary_size)
        return result

    def generate(self):
        """
        Generates the plot and all its subplot.

        If the output path is `None`, will show the plot instead of saving it.
        """
        nrows, ncols = self.get_grid()
        width = ncols * DEFAULT_PLOT_WIDTH
        height = nrows * DEFAULT_PLOT_HEIGHT
        fig, axs = plt.subplots(
            nrows, ncols, sharex=True, sharey=True, figsize=(width, height)
        )
        # Axes are a numpy ndarray with 2 dimensions: rows and columns, it needs to be flattened first just in case
        # If there's only 1 row, flatten will return the same array
        axes = axs.flatten()
        for i, plot in enumerate(self.plots):
            plot.generate(axes[i])
        self.configuration.apply_to_figure(fig)
        if self.output_path is not None:
            plt.savefig(self.output_path)
            plt.close()
        else:
            plt.show()
