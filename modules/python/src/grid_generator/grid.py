from dataclasses import dataclass

from .shapes import Shape


@dataclass
class Cell:
  """
  Programmative representation of a cell.
  """
  bg_color = None
  content: list[Shape] = []


class Grid:
  """
  Programmative representation of a grid.
  """

  def __init__(self):
    self.grid: list[list[Cell]] = []
