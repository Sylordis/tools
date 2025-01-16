from abc import ABC
from dataclasses import dataclass

from .color import Color
from .symbols import OrientationSymbol


@dataclass
class Shape(ABC):
  border_color: Color|None = None
  border_width: int = 0
  fill: Color|None = None
  position:tuple[int,int]|None = None
  height = None
  width = None

@dataclass
class Arrow(Shape):
  orientation: OrientationSymbol|None = None

@dataclass
class Circle(Shape):
  pass
