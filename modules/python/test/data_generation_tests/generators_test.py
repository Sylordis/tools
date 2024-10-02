import math
from pandas import pandas as pd, Series
import pytest
import string

from data_generation.generators import Generators, SingleGenerators


TOLERANCE=0.05
"Tolerance for tests."


def __check_with_tolerance(a, b) -> bool:
  return math.isclose(a, b, rel_tol=TOLERANCE)


@pytest.mark.parametrize(
    "nsamples,mu,max_mu_factor",
    [
      (1, None, 1.0),
      (200, None, 1.0),
      (1000, None, 1.0),
      (1500, 5, 1.0),
      (1500, None, 10),
      (1500, 1.0, 10)
    ]
)
def test_generators__normal_distribution(nsamples, mu, max_mu_factor):
  generated = Generators.normal_distribution(nsamples, mu, max_mu_factor=max_mu_factor)
  series =  pd.Series(generated)
  if mu is None and max_mu_factor is not None:
    assert series.mean() <= max_mu_factor
    assert series.mean() >= -max_mu_factor
  elif mu is None:
    assert series.mean() <= 1.0
    assert series.mean() >= -1.0
  else:
    assert __check_with_tolerance(series.mean(), mu), f"Provided mu ({mu}) should be close to the series' mean ({series.mean()})"
  assert len(generated) == nsamples


@pytest.mark.parametrize(
    "length,population,random_length",
    [
      (3, string.printable, False),
      (10, string.printable, False),
      (10, string.printable, True),
      (3, string.ascii_letters, True),
      (8, string.digits, True),
    ]
)
def test_single_generators__random_str(length, population, random_length):
  result = SingleGenerators.random_str(length, population)
  assert set(result) <= set(population)
  if random_length:
    assert len(result) <= length
  else:
    assert len(result) == length
