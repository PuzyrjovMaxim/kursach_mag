def encode(routes):

    chromosome = []

    for route in routes:

        chromosome.extend(route)

    return chromosome

def decode(chromosome, instance):

    depot = instance.depot

    matrix = instance.distance_matrix

    routes = []

    current_route = []

    current_load = 0

    current_time = 0.0

    previous = depot

    for client in chromosome:

        travel_time = matrix.get(
            previous.id,
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

        capacity_violation = (
            current_load +
            client.demand >
            instance.vehicle_capacity
        )

        time_violation = (
            service_start >
            client.due_date
        )

        if (
            capacity_violation
            or
            time_violation
        ):

            if current_route:

                routes.append(
                    current_route
                )

            current_route = [client]

            current_load = client.demand

            travel_time = matrix.get(
                depot.id,
                client.id
            )

            arrival_time = travel_time

            service_start = max(
                arrival_time,
                client.ready_time
            )

            current_time = (
                service_start +
                client.service_time
            )

            previous = client

        else:

            current_route.append(
                client
            )

            current_load += (
                client.demand
            )

            current_time = (
                service_start +
                client.service_time
            )

            previous = client

    if current_route:

        routes.append(
            current_route
        )

    return routes