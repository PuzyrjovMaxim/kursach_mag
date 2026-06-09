import random

def flatten(routes):

    result = []

    for route in routes:
        result.extend(route)

    return result

def ordered_crossover(
        parent1,
        parent2
):

    size = len(parent1)

    left, right = sorted(
        random.sample(
            range(size),
            2
        )
    )

    child = [None] * size

    child[left:right] = (
        parent1[left:right]
    )

    pointer = right

    for gene in parent2:

        if gene in child:
            continue

        if pointer >= size:
            pointer = 0

        child[pointer] = gene

        pointer += 1

    return child