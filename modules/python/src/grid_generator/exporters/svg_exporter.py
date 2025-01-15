import logging
from pathlib import Path
import svg

from .exporter import Exporter
from ..grid import Grid, GridConfig


class SVGExporter(Exporter):
  """
  Exporter to SVG format.
  """

  def __init__(self):
    self._log = logging.getLogger(__class__.__name__)

  def export(self, grid: Grid, cfg: GridConfig, output_file: Path):
    self._log.debug(f"Creating grid image to {output_file}")
    heightn = len(grid.content)
    widthn = len(grid.content[0])
    height_img = heightn * cfg.cell_size + cfg.border_width
    width_img = widthn * cfg.cell_size + cfg.border_width
    self._log.debug(f"Grid size: {widthn}x{heightn} => Image size: {width_img}x{height_img} px")
    elements: list[svg.Element] = []
    elements.extend(self.create_grid_elements(grid, cfg))
    elements.extend(self.create_svg_elements(grid))
    canvas = svg.SVG(
      width=width_img,
      height=height_img,
      elements = elements
    )
    self._log.debug("Creating resulting file")
    with open(output_file, "w") as write_file:
      write_file.write(str(canvas))

  def create_grid_elements(self, grid: Grid, cfg: GridConfig) -> list[svg.Element]:
    """
    Creates the grid base for the svg.

    :param grid: object representation of the grid
    :param cfg: base configuration of the grid
    """
    svg_path = svg.Path(fill="none", stroke="black", stroke_width=cfg.border_width, d=[f"M {cfg.cell_size} 0 L 0 0 0 {cfg.cell_size}"])
    svg_pattern = svg.Pattern(id="grid", patternUnits = "userSpaceOnUse", width = cfg.cell_size, height = cfg.cell_size, elements=[svg_path])
    svg_defs = svg.Defs(elements=[svg_pattern])
    rect = svg.Rect(width="100%", height="100%", fill="url(#grid)")
    return [svg_defs, rect]

  def create_svg_elements(self, grid: Grid) -> list[svg.Element]:
    """
    :param grid: grid to create the svg elements from
    :return: 
    """
    elements: list[svg.Element] = []
    for y in range(len(grid.content)):
      for x in range(len(grid.content[y])):
        for shape in grid.content[y][x].content:
          self._log.debug(shape)
          # TODO convert shapes into SVG code https://pypi.org/project/svg.py/
    return elements
