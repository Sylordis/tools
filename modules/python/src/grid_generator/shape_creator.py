import logging
import re
from typing import Any


from .shapes import Shape, Arrow, Circle
from .symbols import GridSymbols, ShapeSymbols


class ShapeCreator:

  def __init__(self):
    """
    Creates a new drawing tool.

    :param dist_dir: destination dir for generating the images
    """
    self._log = logging.getLogger()

  def interpret_and_create_shapes(self, n, shape_id, shape_cfg) -> list[Shape]:
    """
    Interprets the shape based on provided groups.

    :param n: number of times to repeat this shape (default will be 1).
    :param shape_id: quick id of the shape as defined in symbols.
    :param shape_cfg: configuration of the shapes to be created (if any).
    :return: a list of shapes
    """
    shape:Shape|None = None
    if not n:
      n = 1
    if shape_cfg:
      shape_cfg = shape_cfg[1:-1].split(GridSymbols.PARAMS_SEPARATOR)
    self._log.debug(f"shape: x{n}, {shape_id}, {shape_cfg}")
    cfg = self.interpret_cfg(shape_cfg)
    match shape_id:
      case ShapeSymbols.ARROW:
        shape = Arrow(**cfg)
      case ShapeSymbols.CIRCLE:
        shape = Circle(**cfg)
      case _:
        self._log.error(f"Unknown shape ID '{shape_id}'.")
    return [shape] * n

  def interpret_cfg(self, shape_cfg_txt: list[str]) -> dict[str,Any]:
    cfg:dict[str,Any] = {}
    for param in shape_cfg_txt:
      match = re.match("([a-z-]+)=(.*)", param)
      if match:
        cfg[match.group(1).replace('-','_')] = match.group(2)
      else:
        self._log.debug(param)
    # TODO
    self._log.debug(cfg)
    return self.convert_cfg_values(cfg)

  def convert_cfg_values(self, old_cfg) -> dict[str,Any]:
    cfg:dict[str,Any] = old_cfg
    # TODO replace properties that has to be replaced
    return cfg