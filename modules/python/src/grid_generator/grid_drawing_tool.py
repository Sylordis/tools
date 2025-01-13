from dataclasses import dataclass
import logging
from pathlib import Path
import re
import svg


from .color import Color
from .grid import Cell, Grid, GridConfig
from .shapes import Shape
from .symbols import GridSymbols


@dataclass
class ToolConfig:
  "Color mode for the image."
  output_format = "SVG"


class GridDrawingTool:
  """
  Main class to draw grids and arrows.
  """

  def __init__(self, dist_dir: Path|None = None):
    """
    Creates a new drawing tool.

    :param grid_cfg: configuration for the tool
    :param dist_dir: destination dir for generating the images
    """
    self._log = logging.getLogger(__class__.__name__)
    self.dist_dir: Path|None = dist_dir

  def draw_all(self, files_str: list[str], cfg: GridConfig = None):
    """
    Tries to draw all provided files.

    :param files_str: list of string paths of files to generate images of
    """
    print(files_str)
    files: list[tuple[Path,Path]] = []
    # Check input files and convert
    for file_str in files_str:
      src_file = Path(file_str).resolve()
      if not src_file.exists():
        self._log.warning(f"File '{src_file}' does not exist. Skipping.")
      else:
        dist_file = self.dist_dir if self.dist_dir is not None else src_file.parent
        dist_file = dist_file / f"{src_file.name}.png"
        files.append((src_file, dist_file))
    # Draw
    for input,output in files:
      grid_config = GridConfig() if cfg is None else cfg
      try:
        self.draw_grid(input, output, grid_config)
      except Exception as e:
        self._log.error("Error while processing the grid:", e)

  def draw_grid(self, input_file: Path, output_file: Path, cfg: GridConfig):
    """
    Draws a grid from a file.

    :param input_file: input text file
    :param output_file: output image file
    """
    self._log.debug(f"{input_file} => {output_file}")
    grid = self.parse_grid_file(input_file)
    self.create_grid_image(grid, cfg, output_file)

  def create_grid_image(self, grid: Grid, cfg:GridConfig, output_file: Path):
    """
    Creates an image from a grid object.

    :param grid: object representation of the grid
    :param output_file: output image file
    """
    self._log.debug(f"Creating grid image to {output_file}")
    heightn = len(grid.content)
    widthn = len(grid.content[0])
    height_img = heightn * cfg.cell_size + (heightn+1) * cfg.border_width
    width_img = widthn * cfg.cell_size + (widthn+1) * cfg.border_width
    self._log.debug(f"Grid size: {widthn}x{heightn} => Image size: {width_img}x{height_img} px")
    elements: list[svg.Element] = self.create_svg_elements(grid)
    canvas = svg.SVG(
      width=width_img,
      height=height_img,
      elements = elements
    )
    print(canvas)

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

  def parse_grid_file(self, file: Path) -> Grid:
    """
    Creates an object representation of the grid provided in a file.

    :param file: file to read
    :return: a grid object
    """
    with open(file, newline='') as grid_file:
      grid:Grid = Grid()
      for line in grid_file:
        line_txt = line.rstrip()
        cells_str = [cell.strip() for cell in line_txt.split(GridSymbols.CELL_SEPARATOR)]
        self._log.debug(cells_str)
        cells = []
        for cell_str in cells_str:
          cell = self.parse_cell(cell_str)
          cells.append(cell)
        grid.content.append(cells)
        self._log.debug(cells)
      return grid

  def parse_cell(self, cell_text: str) -> Cell:
    """
    Parses a cell text to create a Cell and its content.

    :param cell_text: text to parse
    :return: a cell object
    """
    cell = Cell()
    self._log.debug(f"parsing cell: '{cell_text}'")
    if len(cell_text) > 0:
      pattern = r"^(\{[^}]+\})?([0-9]*[A-Za-z]+(\{[^}]+\})?)?(;[0-9]*[A-Za-z]+(\{[^}]+\})?)*$"
      match = re.match(pattern, cell_text)
      if match:
        for txt in list(match.groups()):
          print(txt)
        # TODO
    return cell
