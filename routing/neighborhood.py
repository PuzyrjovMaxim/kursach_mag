import copy


def swap(
        route,
        i,
        j
):

    new_route = copy.deepcopy(
        route
    )

    (
        new_route[i],
        new_route[j]
    ) = (
        new_route[j],
        new_route[i]
    )

    return new_route

def relocate(
        route,
        from_index,
        to_index
):

    new_route = route[:]

    client = new_route.pop(
        from_index
    )

    new_route.insert(
        to_index,
        client
    )

    return new_route

def two_opt(
        route,
        i,
        j
):

    return (
            route[:i]
            +
            route[i:j + 1][::-1]
            +
            route[j + 1:]
    )