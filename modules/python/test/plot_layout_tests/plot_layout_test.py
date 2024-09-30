import pytest

from plot_layout import (
    Orientation,
    Plot,
    PlotLayout,
    LayoutExpansionPolicy,
)


@pytest.fixture
def plot():
    Plot.__abstractmethods__ = set()
    return Plot()


def test_get_grid__specified_grid_is_too_small(plot):
    layout = PlotLayout([plot] * 15)
    layout.configuration.grid = (2, 2)
    with pytest.raises(ValueError):
        layout.get_grid()


@pytest.mark.parametrize(
    "orientation,n_plots,expected_rows,expected_cols",
    [
        # Default orientation (SQUARE)
        (None, 3, 2, 2),  # Default orientation (SQUARE) but minimum plots amount not reached
        (None, 9, 3, 3),  # Default orientation SQUARE
        (None, 81, 9, 9),  # Default orientation SQUARE with large amount
        (None, 32, 6, 6),  # Default orientation SQUARE with non exact square shape
        # Specify Square orientation
        (Orientation.SQUARE, 3, 2, 2),  # Square orientation but minimum plots amount not reached
        (Orientation.SQUARE, 9, 3, 3),  # Square orientation
        (Orientation.SQUARE, 81, 9, 9),  # Square orientation with large amount
        (Orientation.SQUARE, 32, 6, 6),  # Square orientation with non exact square shape
        # X orientation
        (Orientation.X_AXIS, 2, 1, 2),  # X orientation but minimum threshold not reached
        (Orientation.X_AXIS, 5, 2, 4),  # X orientation
        (Orientation.X_AXIS, 9, 2, 5),  # X orientation
        (Orientation.X_AXIS, 91, 7, 13),  # X orientation with large amount
        # Y orientation
        (Orientation.Y_AXIS, 3, 3, 1),  # Y orientation but minimum threshold not reached
        (Orientation.Y_AXIS, 5, 4, 2),  # Y orientation
        (Orientation.Y_AXIS, 9, 5, 2),  # Y orientation
        (Orientation.Y_AXIS, 91, 13, 7),  # Y orientation with large amount
    ],
)
def test_get_grid__default_policy(
    plot, orientation: Orientation | None, n_plots: int, expected_rows: int, expected_cols: int
):
    list_of_plots: list[Plot] = [plot] * n_plots
    layout = PlotLayout(list_of_plots)
    if orientation is not None:
        layout.configuration.orientation = orientation
    grid = layout.get_grid()
    assert grid == (expected_rows, expected_cols)


@pytest.mark.parametrize(
    "orientation,policy,n_plots,expected_rows,expected_cols",
    [
        (Orientation.SQUARE, LayoutExpansionPolicy.minus(1, 3), 8, 3, 3),  # SQUARE doesn't care about policy
        (Orientation.X_AXIS, LayoutExpansionPolicy.minus(6, 3), 5, 1, 5),  # Number of plots lower than policy minimum
        (Orientation.X_AXIS, LayoutExpansionPolicy.minus(5, 2), 8, 2, 5),
        (Orientation.X_AXIS, LayoutExpansionPolicy.minus(5, 1), 66, 8, 9),
        # Major size will be 9 (bigger than 8x7) but we don't need 8 lines on minor, only 7
        (Orientation.X_AXIS, LayoutExpansionPolicy.minus(5, 1), 57, 7, 9),
        # Major size will be 9 (bigger than 8x7) but we don't need 8 lines on minor, only 7 (just about)
        (Orientation.X_AXIS, LayoutExpansionPolicy.minus(5, 1), 63, 7, 9),
        (Orientation.Y_AXIS, LayoutExpansionPolicy.divided_ceil(3, 3), 70, 14, 5),
    ],
)
def test_get_grid__custom_policy(
    plot,
    orientation: Orientation | None,
    policy: LayoutExpansionPolicy | None,
    n_plots: int,
    expected_rows: int,
    expected_cols: int,
):
    list_of_plots: list[Plot] = [plot] * n_plots
    layout = PlotLayout(list_of_plots)
    layout.configuration.expansion_policy = policy
    if orientation is not None:
        layout.configuration.orientation = orientation
    grid = layout.get_grid()
    assert grid == (expected_rows, expected_cols)


@pytest.mark.parametrize(
    "provided_grid,orientation,n_plots",
    [
        ((3, 5), None, 10),
        ((10, 10), None, 5),
        ((1000, 100), None, 99),
        ((3, 5), Orientation.X_AXIS, 10),
        ((10, 10), Orientation.Y_AXIS, 5),
        ((1000, 100), Orientation.Y_AXIS, 99),
    ],
)
def test_get_grid__with_override(
    plot, provided_grid: tuple[int, int] | None, orientation: Orientation | None, n_plots: int
):
    """
    This test verifies that the grid override attribute actually overrides the auto layouting.
    """
    list_of_plots: list[Plot] = [plot] * n_plots
    layout = PlotLayout(list_of_plots)
    if provided_grid is not None:
        layout.configuration.grid = provided_grid
    if orientation is not None:
        layout.configuration.orientation = orientation
    grid = layout.get_grid()
    assert grid == provided_grid
