from abc import ABC, abstractmethod
from matplotlib.axes import Axes

from .plot_configuration import PlotConfiguration


class Plot(ABC):
    """
    Abstract generic plot class with `generate` being the main method.
    """

    def __init__(self, plot_cfg: PlotConfiguration | None = None):
        self.plot_cfg = plot_cfg if plot_cfg is not None else PlotConfiguration()

    @abstractmethod
    def generate(self, axis: Axes):
        """
        Generates the plot on a given axis.
        In case of a layout plot, this method is used to setup each subplot, please override it and call this parent one.
        ```
        super().generate(axis)
        ```

        :param axis: axes to generate the plot on
        """
        self.plot_cfg.apply_to_axis(axis)
