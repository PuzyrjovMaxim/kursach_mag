from models.client import Client


def check_capacity(
    route: list[Client],
    vehicle_capacity: int
) -> bool:

    load = sum(
        client.demand
        for client in route
    )

    return (
        load <=
        vehicle_capacity
    )


def check_time_windows(
    depot: Client,
    route: list[Client],
    distance_matrix
) -> bool:

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

        if service_start > client.due_date:

            return False

        current_time = (
            service_start +
            client.service_time
        )

        current_node = client

    return_time = (
        current_time +
        distance_matrix.get(
            current_node.id,
            depot.id
        )
    )

    return (
        return_time <=
        depot.due_date
    )


def is_route_feasible(
    depot: Client,
    route: list[Client],
    vehicle_capacity: int,
    distance_matrix
) -> bool:

    return (
        check_capacity(
            route,
            vehicle_capacity
        )
        and
        check_time_windows(
            depot,
            route,
            distance_matrix
        )
    )