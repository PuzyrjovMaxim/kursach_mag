import random

def tournament_selection(
        population,
        fitness,
        tournament_size=3
):

    candidates = random.sample(
        list(
            zip(
                population,
                fitness
            )
        ),
        tournament_size
    )

    candidates.sort(
        key=lambda x: x[1]
    )

    return candidates[0][0]