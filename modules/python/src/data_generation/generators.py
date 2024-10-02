import numpy as np
import random
import string


class Generators:
    "Contains different data generator that can be used as Callables to generate multiple samples."

    @staticmethod
    def normal_distribution(
        nsamples: int,
        mu: float | None = 0.0,
        sigma: float | None = None,
        max_mu_factor: float = 1.0
    ) -> list:
        """
        Generates samples according to a normal distribution (ref: https://en.wikipedia.org/wiki/Normal_distribution).

        :param nsamples: number of samples to generate.
        :param mu: mean value offset, random if None. Default is 0.
        Standard normal distributions happen for mu = 0.
        Random if `None` is provided (e.g.: [-1,1] * max_mu_factor).
        :param sigma: variance of the values. The higher, the flatter and wider your distribution will be. Default is random [0,1].
        :param max_mu_factor: multiplier for mu representing the biggest possible mu, only if mu is not specified.
        :return: list of n samples from the distribution
        """
        rand = np.random.default_rng()
        mu_real = random.uniform(-1,1) * max_mu_factor if mu is None else mu
        sigma_real = rand.random() if sigma is None else sigma
        generated = mu_real + sigma_real * rand.standard_normal(nsamples)
        return generated


class SingleGenerators:
    "Contains different data generator that can be used as Callables to generate a single value."

    @staticmethod
    def random_str(length: int, population, random_length: bool = False) -> str:
        """
        Generates a random string.

        :param length: length of each string
        :param population: population of letters authorised to generate from, used by https://docs.python.org/3/library/random.html#random.choice
        :param random_length: if set to `True`, the generated string will have a length up to the provided length
        :return: a random string
        """
        real_length = length
        if random_length:
            real_length = random.randrange(1, length)
        return "".join(random.choices(population, k=real_length))

    @staticmethod
    def random_tla() -> str:
        """
        Generates a random TLA (Three Letters Acronym) string (3 letters uppercase strings).

        :return: one TLA
        """
        return SingleGenerators.random_str(3, string.ascii_uppercase)
