from dataclasses import dataclass
import logging
from pathlib import Path
import PIL

from .grid import Cell, Grid
from .shapes import Shape
from .symbols import GridSymbols


@dataclass
class DrawToolConfig:
  bg_color: str = "transparent"
  shapes_color: str = "#FF0000"
  grid_size: int = 15
  grid_color: str = "#000000"
  image_mode = "RGB"
  output_format = "PNG"


class GridDrawingTool:
  """
  Main class to draw grids and arrows.
  """

  def __init__(self, grid_cfg: DrawToolConfig = None, dist_dir: Path|None = None):
    """
    Creates a new drawing tool.

    :param grid_cfg: configuration for the tool
    :param dist_dir: destination dir for generating the images
    """
    self._log = logging.getLogger(__class__.__name__)
    self.grid_cfg: DrawToolConfig = DrawToolConfig() if grid_cfg is None else grid_cfg
    self.dist_dir: Path|None = dist_dir

  def draw_all(self, files_str: list[str]):
    """
    Tries to draw all provided files.

    :param files_str: list of string paths of files to generate images of
    """
    files: list[tuple[Path,Path]] = []
    # Check input files and convert
    for file_str in files_str:
      src_file = Path(file_str).resolve()
      if not src_file.exists():
        self._log.warning(f"File '{src_file}' does not exist. Skipping.")
      else:
        dist_file = self.dist_dir if self.dist_dir is not None else src_file.parent
        dist_file = dist_file / src_file.name / ".png"
        files.append((src_file, dist_file))
    # Draw
    for input,output in files:
      try:
        self.draw_grid(input, output)
      except Exception as e:
        self._log.error("Error while processing the grid:", e)

  def draw_grid(self, input_file: Path, output_file: Path):
    """
    Draws a grid from a file.

    :param input_file: input text file
    :param output_file: output image file
    """
    self._log.debug(f"{input_file} => {output_file}")
    grid = self.parse_grid_file(input_file)
    self.create_grid_image(grid, output_file)

  def create_grid_image(self, grid: Grid, output_file: Path):
    """
    Creates an image from a grid object.

    :param grid: object representation of the grid
    :param output_file: output image file
    """
    # TODO

  def parse_grid_file(self, file: Path) -> Grid:
    """
    Creates an object representation of the grid provided in a file.

    :param file: file to read
    :return: a grid object
    """
    with open(file, newline='') as grid_file:
      for line in grid_file:
        line_txt = line.rstrip()
        cells_str = [cell.strip() for cell in line_txt.split(GridSymbols.CELL_SEPARATOR)]
        self._log.debug(cells_str)
        cells = []
        for cell_str in cells_str:
          cell = Cell()
          cells.append(cell)
    # TODO

