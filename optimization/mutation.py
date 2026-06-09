import random

from optimization.neighborhood import (
    swap,
    relocate
)

def swap_mutation(routes):

    new_routes = [
        route[:]
        for route in routes
    ]

    route = random.choice(
        new_routes
    )

    if len(route) < 2:
        return new_routes

    i, j = sorted(
        random.sample(
            range(len(route)),
            2
        )
    )

    route[:] = swap(
        route,
        i,
        j
    )

    return new_routes

def relocate_mutation(routes):

    new_routes = [
        route[:]
        for route in routes
    ]

    route = random.choice(
        new_routes
    )

    if len(route) < 2:
        return new_routes

    i, j = sorted(
        random.sample(
            range(len(route)),
            2
        )
    )

    route[:] = relocate(
        route,
        i,
        j
    )

    return new_routes