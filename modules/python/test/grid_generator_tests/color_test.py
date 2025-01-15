import pytest

from grid_generator.color import Color


@pytest.mark.parametrize(
    ("input","expected"),
    [
        ([0, 0, 0, 0], (0, 0, 0, 0)),
        ([255, 255, 255, 255], (1., 1., 1., 1.)),
        (["FF0000"], (1., 0., 0., 1.)),
        (["#FF0000"], (1., 0., 0., 1.)),
        (["#00FF00"], (0., 1., 0., 1.)),
        (["#0000FF"], (0., 0., 1., 1.)),
    ])
def test_color(input,expected):
    color = Color(*input)
    assert expected == (color.red, color.green, color.blue, color.opacity)

@pytest.mark.parametrize("input",
    [
        ([255,300,0,0]),
        ([-2,0,0,0])
    ])
def test_color__with_exception(input):
    with pytest.raises(ValueError):
        Color(*input)
