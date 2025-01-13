from __future__ import annotations

INT_BASE = 255
COLORS_DICT: dict[str,str] = {
    "black": "#000000",
    "blue": "#0000FF",
    "green": "#00FF00",
    "red": "#FF0000",
    "white": "#FFFFFF",
}

class Color:

    def __init__(self, value:str|tuple|list|float=None, green:float = 0.0, blue:float = 0.0, opacity:float = 1.0):
        self.opacity = opacity
        if isinstance(value, float):
            self.red, self.green, self.blue, self.opacity = value, green, blue, opacity
        if isinstance(value, list):
            self.red, self.green, self.blue, self.opacity, *_ = value + [1.0, 1.0, 1.0, 1.0]
        if isinstance(value, tuple):
            self.red, self.green, self.blue, self.opacity, *_ = value + (1.0, 1.0, 1.0, 1.0)
        if isinstance(value, str) and value[0] == '#':
            self.red, self.green, self.blue = self.web_to_rgb(value)

    def __iter__(self):
        yield self.red
        yield self.green
        yield self.blue
        yield self.opacity

    @staticmethod
    def from_rgb(red:int = 0, green:int = 0, blue:int = 0, opacity:int = INT_BASE) -> Color:
        assert 0 <= red <= INT_BASE and 0 <= green <= INT_BASE and 0 <= blue <= INT_BASE
        return Color(float(red)/INT_BASE, float(green)/INT_BASE, float(blue)/INT_BASE, float(opacity)/INT_BASE)

    @classmethod
    def web_to_rgb(cls, color:str) -> tuple:
        assert color is not None
        string = color.lower()
        if string[0] == "#":
            string = string[1:]
        r,g,b = int(string[0:1], 16), int(string[2:3], 16), int(string[4:5], 16)
        return r,g,b

    @staticmethod
    def from_web(hex_string:str) -> Color:
        assert hex_string is not None
        string = hex_string.lower()
        if string[0] == "#":
            string = string[1:]
        r,g,b = int(string[0:1], 16), int(string[2:3], 16), int(string[4:5], 16)
        return Color(r,g,b)

    @staticmethod
    def from_name(name:str) -> Color:
        return Color.from_web(COLORS_DICT.get(name, None))

    def to_web(self) -> str:
        return "#%02s%02s%02s".format(hex(self.red), hex(self.green), hex(self.blue))
