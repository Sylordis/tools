from enum import Enum


class Orientation:

    def __init__(self, shortcut:str, rotation:int):
        self.shortcut = shortcut
        self.rotation = rotation


class OrientationKey(Enum):
    BOTTOM = 1
    DIAGONAL_BOTTOM_LEFT = 2
    DIAGONAL_BOTTOM_RIGHT = 3
    DIAGONAL_TOP_LEFT = 4
    DIAGONAL_TOP_RIGHT = 5
    LEFT = 6
    RIGHT = 7
    TOP = 8


ORIENTATIONS: dict[OrientationKey,Orientation] = {
    OrientationKey.BOTTOM: Orientation("B", 90),
    OrientationKey.DIAGONAL_BOTTOM_LEFT: Orientation("Z", 135),
    OrientationKey.DIAGONAL_BOTTOM_RIGHT: Orientation("C", 45),
    OrientationKey.DIAGONAL_TOP_LEFT: Orientation("Q", 225),
    OrientationKey.DIAGONAL_TOP_RIGHT: Orientation("E", 315),
    OrientationKey.LEFT: Orientation("L", 180),
    OrientationKey.RIGHT: Orientation("R", 0),
    OrientationKey.TOP: Orientation("T", 270),
}
