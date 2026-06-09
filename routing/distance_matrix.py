from models.client import Client

from routing.distance import (
    euclidean_distance
)


class DistanceMatrix:

    def __init__(
            self,
            nodes: list[Client]
    ):

        self.nodes = nodes

        self.id_to_index = {
            node.id: index
            for index, node in enumerate(nodes)
        }

        self.matrix = self._build()

    def _build(self):

        size = len(self.nodes)

        matrix = [
            [0.0] * size
            for _ in range(size)
        ]

        for i in range(size):

            for j in range(i + 1, size):

                dist = euclidean_distance(
                    self.nodes[i],
                    self.nodes[j]
                )

                matrix[i][j] = dist
                matrix[j][i] = dist

        return matrix

    def get(
            self,
            from_id: int,
            to_id: int
    ) -> float:

        i = self.id_to_index[from_id]
        j = self.id_to_index[to_id]

        return self.matrix[i][j]