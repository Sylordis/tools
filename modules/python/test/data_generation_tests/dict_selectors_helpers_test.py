import pytest
from pandas import DataFrame

from data_generation.selectors_helpers import DictSelectorHelpers


@pytest.fixture
def dataseries() -> DataFrame:
  return DataFrame(data = {
    'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    'y': [0.5, 3.14, 9.12, -0.13, 0.0, -15.0823, -199.20, 182, 92.23, 5.12],
  })

@pytest.mark.parametrize(
    "series_name,transformer,expected",
    [
      ("x", max, 9),
      ("x", min, 0),
      ("x", None, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
      ("y", lambda l : [x for x in l if x > 3 and x <= 180], [3.14, 9.12, 92.23, 5.12]),
    ]
)
def test_of_series(dataseries: DataFrame, series_name: str, transformer, expected):
  selector = DictSelectorHelpers.of_series(series_name, transformer)
  result = selector(dataseries)
  if type(expected) is list:
    result = list(result)
  assert expected == result
