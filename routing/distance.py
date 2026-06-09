from math import sqrt

from models.client import Client


def euclidean_distance(
        a: Client,
        b: Client
) -> float:

    return sqrt(
        (a.x - b.x) ** 2 +
        (a.y - b.y) ** 2
    )