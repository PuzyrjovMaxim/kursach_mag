from routing.route_utils import route_distance


PENALTY_CAPACITY = 1000

PENALTY_TIME_WINDOW = 1000

PENALTY_UNSERVED = 5000

PENALTY_EXTRA_VEHICLE = 10000


def evaluate_route(instance, route):

    depot = instance.depot

    matrix = instance.distance_matrix

    load = 0

    current_time = 0.0

    previous = depot

    distance = 0.0

    penalty = 0.0

    for client in route:

        load += client.demand

        travel_time = matrix.get(
            previous.id,
            client.id
        )

        distance += travel_time

        arrival_time = (
            current_time +
            travel_time
        )

        service_start = max(
            arrival_time,
            client.ready_time
        )

        #
        # Проверка временного окна клиента
        #

        if service_start > client.due_date:

            penalty += (
                service_start -
                client.due_date
            ) + PENALTY_TIME_WINDOW

        current_time = (
            service_start +
            client.service_time
        )

        previous = client

    #
    # Возврат в депо
    #

    return_travel_time = matrix.get(
        previous.id,
        depot.id
    )

    distance += return_travel_time

    return_time = (
        current_time +
        return_travel_time
    )

    #
    # Проверка временного окна депо
    #

    if return_time > depot.due_date:

        penalty += (
            return_time -
            depot.due_date
        ) + PENALTY_TIME_WINDOW

    #
    # Проверка вместимости
    #

    if load > instance.vehicle_capacity:

        penalty += (
            load -
            instance.vehicle_capacity
        ) + PENALTY_CAPACITY

    return distance, penalty


def evaluate_solution(
    instance,
    routes
):

    total_distance = 0.0

    total_penalty = 0.0

    served_clients = 0

    for route in routes:

        distance, penalty = evaluate_route(
            instance,
            route
        )

        total_distance += distance

        total_penalty += penalty

        served_clients += len(route)

    unserved_clients = (
        len(instance.clients)
        - served_clients
    )

    if unserved_clients > 0:

        total_penalty += (
            unserved_clients *
            PENALTY_UNSERVED
        )

    extra_vehicles = (
        len(routes)
        - instance.vehicle_count
    )

    if extra_vehicles > 0:

        total_penalty += (
            extra_vehicles *
            PENALTY_EXTRA_VEHICLE
        )

    return (
        total_distance,
        total_penalty
    )


def total_cost(
    instance,
    routes
):

    distance, penalty = evaluate_solution(
        instance,
        routes
    )

    return distance + penalty