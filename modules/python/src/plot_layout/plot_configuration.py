from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import numpy as np
from matplotlib.axes import Axes
from matplotlib.ticker import Formatter
from typing import Any, Callable, Literal, TypeAlias


LABEL_NO_LEGEND = "_no_legend"
"Constant for labels that should be hidden in the legend."


class Orientation(StrEnum):

    X_AXIS = "x"
    "Orientation on X or Horizontal Axis."
    Y_AXIS = "y"
    "Orientation on Y or Vertical Axis."
    SQUARE = "square"
    """
    Square orientation, which is a combined Horizontal and Vertical with a default on Horizontal.
    A Square layout will be as equal as possible on all axes.
    """


AxisOrientation: TypeAlias = Literal[Orientation.X_AXIS, Orientation.Y_AXIS]
"Usual orientation for axes, i.e. X/horizontal or Y/vertical. This is a subset of the Orientation enum."

@dataclass
class PlotBins:
    """
    Holds a bins configuration.

    Attributes
    ---------
    minimum: float | None
      Minimum bins for the axis. Default is None.
    maximum: float | None
      Maximum bins for the axis. Default is None.
    step: float | None
      Bins step for the axis. Default is None.
    tick_formatter: Callable[[Any],str] | None
      Bin tick formatter for the axis, converting every step of the range to a string usable by matplotlib.
      Default is None, which will leave matplotlib format it automatically.
    """

    minimum: float | None = None
    "Minimum bins for the axis."
    maximum: float | None = None
    "Maximum bins for the axis."
    step: float | None = None
    "Bins step for the axis, one needs to specify a tick formatter to have text on the axis."
    tick_formatter: Callable[[Any], str] | None = None
    """
    Bin tick formatter for the axis, converting every step of the range to a string usable by matplotlib.
    If left to None, matplotlib will format it automatically.
    """

@dataclass
class PlotAxisConfiguration:
    """
    Holds the configuration for a given axis.

    Attributes
    ----------
    orientation : AxisOrientation
      Axis orientation, either "x" or "y". Use the static methods for_x() and for_y() for easier initialisation.
    bins: PlotBins
      Bins for the axis.
    major_formatter: Formatter | None
      Major formatter for the axis. Default is None.
    minor_formatter: Formatter | None
      Minor formatter for the axis. Default is None.
    label: str | None
      Label for the axis. If you're looking to set the axis label for a plot layout, consider updating the PlotLayoutConfiguration labels instead.
      Default is None.
    """

    orientation: AxisOrientation
    "Axis type, either X or Y."
    bins: PlotBins | None = None
    "Bins for the axis."
    major_formatter: Formatter | None = None
    "Major formatter for the axis."
    minor_formatter: Formatter | None = None
    "Minor formatter for the axis."
    label: str | None = None
    """
    Label for the axis. If you're looking to set a common axis label for a plot layout, use its configuration instead.
    ```
    """

    def __post_init__(self):
        if self.bins is None:
            self.bins = PlotBins()

    def __is_x(self) -> bool:
        "Checks if this item is oriented for the X axis or not, for internal business logic."
        return self.orientation == Orientation.X_AXIS

    @staticmethod
    def for_x() -> PlotAxisConfiguration:
        "Create a new axis configuration for the X axis."
        return PlotAxisConfiguration(Orientation.X_AXIS)

    @staticmethod
    def for_y() -> PlotAxisConfiguration:
        "Create a new axis configuration for the Y axis."
        return PlotAxisConfiguration(Orientation.Y_AXIS)

    def apply_to_axis(self, axis: Axes):
        """
        Applies its configuration to provided axis, if provided.

        :param axes: Axis to apply the configuration to
        """
        self._apply_text(axis)
        self._apply_bins(axis)
        self._apply_formatters(axis)

    def _apply_text(self, axis: Axes):
        "Applies label."
        if self.label is not None:
            if self.__is_x():
                axis.set_xlabel(self.label)
            else:
                axis.set_ylabel(self.label)

    def _apply_bins(self, axis: Axes):
        "Applies bin configuration, min, max, steps and labels."
        if self.bins is not None and self.bins.minimum is not None and self.bins.maximum is not None:
            ticks, labels = self._prepare_ticks()
            # Apply to correct axis
            if self.__is_x():
                axis.set_xlim(self.bins.minimum, self.bins.maximum)
                if ticks is not None:
                    axis.set_xticks(ticks, labels=labels)
            else:
                axis.set_ylim(self.bins.minimum, self.bins.maximum)
                if ticks is not None:
                    axis.set_yticks(ticks, labels=labels)

    def _prepare_ticks(self) -> tuple:
        ticks = None
        labels = None
        if self.bins.step is not None:
            ticks = np.arange(self.bins.minimum, self.bins.maximum + 0.1, self.bins.step)
            if self.bins.tick_formatter is not None:
                labels = [self.bins.tick_formatter(a) for a in ticks]
        return ticks, labels

    def _apply_formatters(self, axis: Axes):
        "Applies major and minor formatter if any supplied."
        if self.major_formatter is not None:
            if self.__is_x():
                axis.xaxis.set_major_formatter(self.major_formatter)
            else:
                axis.yaxis.set_major_formatter(self.major_formatter)
        if self.minor_formatter is not None:
            if self.__is_x():
                axis.xaxis.set_minor_formatter(self.minor_formatter)
            else:
                axis.yaxis.set_minor_formatter(self.minor_formatter)


@dataclass
class PlotConfiguration:
    """
    Holds the configuration for a whole single plot or a subplot, regarding axis, colours and other graphical options.

    Warning: this does not manage different series per say.

    Attributes
    ----------
    colors: list | None
      List of colours to override the normal list of colours.
      See https://matplotlib.org/stable/users/explain/colors/colors.html#colors-def.
    line_width: float | None
      Width of the line, e.g. bar width for bar graphs.
    title: str | None
      Title of the plot.
    x: PlotAxisConfiguration
      X axis configuration. Instantiated by default for x but instance can be empty if not set.
    y: PlotAxisConfiguration
      Y axis configuration. Instantiated by default for y but instance can be empty if not set.
    show_legend: bool = True
      Whether the legend should be shown (`True`) or hidden (`False`).
      
      In order to display only one legend for multiple subplots. Set every plot but the first one with `show_legend` to
      `False` in order for this to work.
      If used, make sure that series between plots have the same colours.
    """

    colors: list | None = None
    "List of colours to override the normal list of colours. See https://matplotlib.org/stable/users/explain/colors/colors.html#colors-def."
    line_width: float | None = None
    "Width of the line, e.g. bar width for bar graphs."
    title: str | None = None
    "Title of the plot."
    x: PlotAxisConfiguration = field(default_factory=PlotAxisConfiguration.for_x)
    "X axis configuration. Instantiated by default for x but instance can be empty if not set."
    y: PlotAxisConfiguration = field(default_factory=PlotAxisConfiguration.for_y)
    "Y axis configuration. Instantiated by default for y but instance can be empty if not set."
    show_legend: bool = True
    """
    Whether the legend should be shown (`True`) or hidden (`False`).
    
    In order to display only one legend for multiple subplots. Set every plot but the first one with `show_legend` to
    `False` in order for this to work.
    If used, make sure that series between plots have the same colours.
    """

    def clone(self, **kwargs) -> PlotConfiguration:
        "Produces a clone of itself in order to be reused with almost similar configuration."
        target = PlotConfiguration()
        target.__dict__.update(self.__dict__)
        target.__dict__.update(kwargs)
        return target

    def create_label(self, label: str) -> str:
        """
        Creates the label according to configuration and normal label name. This takes into account the show_legend attribute.

        This method is to be used while creating a series with an argument:
        ```
        label=self.cfg.create_label("your label")
        ```

        :param label: normal label of the series.
        """
        return label if self.show_legend else LABEL_NO_LEGEND

    def apply_to_axis(self, axes: Axes):
        """
        Apply all possible configuration to a provided axes.

        :param axes: axes to apply the configuration to
        """
        self.x.apply_to_axis(axes)
        self.y.apply_to_axis(axes)
        if self.title is not None:
            axes.set_title(self.title)
