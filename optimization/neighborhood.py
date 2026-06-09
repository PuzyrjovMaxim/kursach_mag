import copy

def swap(route, i, j):

    new_route = route[:]

    new_route[i], new_route[j] = (
        new_route[j],
        new_route[i]
    )

    return new_route

def relocate(route, i, j):

    new_route = route[:]

    customer = new_route.pop(i)

    new_route.insert(j, customer)

    return new_route

def two_opt(route, i, j):

    return (
        route[:i]
        +
        route[i:j + 1][::-1]
        +
        route[j + 1:]
    )

def move_customer(
    routes,
    route_a,
    route_b,
    customer_idx,
    insert_idx=None
):

    new_routes = copy.deepcopy(
        routes
    )

    customer = (
        new_routes[route_a].pop(
            customer_idx
        )
    )

    if insert_idx is None:

        new_routes[route_b].append(
            customer
        )

    else:

        new_routes[route_b].insert(
            insert_idx,
            customer
        )

    return new_routes

def inter_route_swap(
    routes,
    route_a,
    idx_a,
    route_b,
    idx_b
):

    new_routes = copy.deepcopy(
        routes
    )

    (
        new_routes[route_a][idx_a],
        new_routes[route_b][idx_b]
    ) = (
        new_routes[route_b][idx_b],
        new_routes[route_a][idx_a]
    )

    return new_routes


def relocate_between_routes(
    routes,
    source_route,
    source_idx,
    target_route,
    target_idx=None
):

    new_routes = copy.deepcopy(
        routes
    )

    customer = (
        new_routes[source_route].pop(
            source_idx
        )
    )

    if target_idx is None:

        new_routes[target_route].append(
            customer
        )

    else:

        new_routes[target_route].insert(
            target_idx,
            customer
        )

    return new_routes