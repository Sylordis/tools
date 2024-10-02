# This is an example on how to generate a multi-plots plot using plot_layout module.
# Usage: python plot_layout_example.py [output]

from __future__ import annotations

import sys

from matplotlib import ticker, pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
from pandas import read_csv, DataFrame

from .plot import Plot
from .plot_configuration import PlotBins, PlotConfiguration
from .plot_layout import PlotLayout, PlotLayoutConfiguration

DATA_PATH = Path("../data")
ANNOTATION_ALIGN_LEFT = (0.05, 0.95)
ANNOTATION_ALIGN_RIGHT = (0.55, 0.95)

class FakeHistogramPlot(Plot):

  def __init__(self, data_csv: Path, stats_csv: Path, plot_cfg: PlotConfiguration | None = None):
    super().__init__(plot_cfg)
    self.data_csv = data_csv
    self.stats_csv = stats_csv

  def generate(self, axis: Axes):
    super().generate(axis)
    total_samples = -1
    y_extremum = 0

    # Data
    with open(self.data_csv, newline='') as datafile:
      datareader = read_csv(datafile)
      ax_data_x = datareader['x'].tolist()
      ax_data_y_full = datareader['entries'].tolist()
      # Make percentages: sum the numbers of entries and find the percentages for each x
      total_samples = sum(ax_data_y_full)
      ax_data_y_percent = [x * 100 / total_samples for x in ax_data_y_full]
      y_extremum = max(ax_data_y_percent)
      axis.bar(ax_data_x, ax_data_y_percent, width=self.plot_cfg.bar_width, color=self.plot_cfg.bar_colors[0], label=self.plot_cfg.create_label("FOO"))

    # Statistics
    with open(self.stats_csv, newline='') as statsfile:
      statsreader: DataFrame = read_csv(statsfile)
      minimum = float(statsreader["Minimum"].to_list()[0])
      maximum = float(statsreader["Maximum"].to_list()[0])
      mean = float(statsreader["Mean"].to_list()[0])
      minimum_tla = str(statsreader["MIN_TLA"].to_list()[0])
      maximum_tla = str(statsreader["MAX_TLA"].to_list()[0])
      other_tla = str(statsreader["TLA"].to_list()[0])
      stats_x = [minimum, mean, maximum]
      stats_y = [y_extremum / 4, y_extremum / 2, y_extremum / 4]
      axis.bar(stats_x, stats_y, width=self.plot_cfg.bar_width, color=self.plot_cfg.bar_colors[1], label=self.plot_cfg.create_label("Bar"))
      # Annotate
      annotation_text = f"Min: {"%.2f" % minimum} at {minimum_tla}\nMax: {"%.2f" % maximum} at {maximum_tla}\nMean: {mean}\nTLA: {other_tla}"
      annotation_coords = ANNOTATION_ALIGN_LEFT if self.plot_cfg.x.bins.maximum is not None and mean >= self.plot_cfg.x.bins.maximum / 2 else ANNOTATION_ALIGN_RIGHT
      axis.annotate(annotation_text, annotation_coords, xycoords="axes fraction", fontsize="small", linespacing=1.5, va="top")


def main() -> int:
  output_path = None
  if len(sys.argv) >= 2:
    output_path = Path(sys.argv[1])
  layout_cfg = PlotLayoutConfiguration()
  layout_cfg.title="Example of Plot Layout"
  layout_cfg.axis_labels=("Common X values", "relative frequency per bin")
  layout = PlotLayout(output_path=output_path, configuration=layout_cfg)

  plot_cfg = PlotConfiguration()
  plot_cfg.y.major_formatter = ticker.PercentFormatter(xmax=100)
  plot_cfg.x.bins = PlotBins(0.0, 5.0)
  plot_cfg.bar_colors = ['tab:blue', 'orangered']
  plot_cfg.bar_width = 0.05

  cfgs = [plot_cfg.clone(title=f"Graph {i}", show_legend=(i == 1)) for i in range(1,7)]

  layout.plots = [
    FakeHistogramPlot(DATA_PATH / "histo1_data.csv", DATA_PATH / "histo1_statistics.csv"),
    FakeHistogramPlot(DATA_PATH / "histo2_data.csv", DATA_PATH / "histo2_statistics.csv"),
    FakeHistogramPlot(DATA_PATH / "histo3_data.csv", DATA_PATH / "histo3_statistics.csv"),
    FakeHistogramPlot(DATA_PATH / "histo3_data.csv", DATA_PATH / "histo3_statistics.csv"),
    FakeHistogramPlot(DATA_PATH / "histo1_data.csv", DATA_PATH / "histo1_statistics.csv"),
    FakeHistogramPlot(DATA_PATH / "histo2_data.csv", DATA_PATH / "histo2_statistics.csv"),
  ]
  for i, plot in enumerate(layout.plots):
    plot.plot_cfg = cfgs[i]
  layout.generate()
