import pytest

from grid_generator.color import Color


@pytest.mark.parametrize(
    "irgbo,ergbo",
    [
        ((0, 0, 0, 0), (0, 0, 0, 0)),
        ((255, 255, 255, 255), (1., 1., 1., 1.)),
    ])
def test_rgb(irgbo,ergbo):
    r,g,b,o = irgbo
    color = Color.rgb(r,g,b,o)
    assert ergbo == (color.red, color.green, color.blue, color.opacity)