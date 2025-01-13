from abc import ABC
from dataclasses import dataclass

from .color import Color

@dataclass
class Shape(ABC):
  border_color: Color|None
  fill_color: Color|None

@dataclass
class Arrow(Shape):
  pass

@dataclass
class Circle(Shape):
  pass
