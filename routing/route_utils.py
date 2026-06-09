from models.client import Client

from routing.feasibility import (
    check_time_windows
)


def route_load(
    route: list[Client]
) -> int:

    return sum(
        client.demand
        for client in route
    )


def route_distance(
    depot: Client,
    route: list[Client],
    distance_matrix
) -> float:

    if not route:
        return 0.0

    total_distance = 0.0

    current = depot

    for client in route:

        total_distance += (
            distance_matrix.get(
                current.id,
                client.id
            )
        )

        current = client

    total_distance += (
        distance_matrix.get(
            current.id,
            depot.id
        )
    )

    return total_distance


def route_completion_time(
    depot: Client,
    route: list[Client],
    distance_matrix
) -> float:

    current_time = 0.0

    current_node = depot

    for client in route:

        travel_time = distance_matrix.get(
            current_node.id,
            client.id
        )

        arrival_time = (
            current_time +
            travel_time
        )

        service_start = max(
            arrival_time,
            client.ready_time
        )

        current_time = (
            service_start +
            client.service_time
        )

        current_node = client

    current_time += distance_matrix.get(
        current_node.id,
        depot.id
    )

    return current_time


def solution_distance(
    depot: Client,
    routes,
    distance_matrix
) -> float:

    total = 0.0

    for route in routes:

        total += route_distance(
            depot,
            route,
            distance_matrix
        )

    return total


def served_clients(
    routes
) -> int:

    return sum(
        len(route)
        for route in routes
    )


def route_penalty(
    depot: Client,
    route: list[Client],
    vehicle_capacity: int,
    distance_matrix
) -> float:

    penalty = 0.0

    load = route_load(
        route
    )

    if load > vehicle_capacity:

        penalty += (
            load -
            vehicle_capacity
        ) * 10000

    if not check_time_windows(
        depot,
        route,
        distance_matrix
    ):

        penalty += 100000

    return penalty