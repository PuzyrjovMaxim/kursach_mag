from dataclasses import dataclass, field

from models.route import Route


@dataclass
class Solution:

    algorithm: str

    routes: list[Route] = field(
        default_factory=list
    )

    total_distance: float = 0.0

    total_penalty: float = 0.0

    execution_time: float = 0.0

    feasible: bool = True

    served_clients: int = 0

    unserved_clients: int = 0

    @property
    def route_count(self) -> int:

        return len(self.routes)

    @property
    def used_vehicles(self) -> int:

        return len(
            [
                route
                for route in self.routes
                if not route.is_empty
            ]
        )

    @property
    def total_cost(self) -> float:

        return (
            self.total_distance +
            self.total_penalty
        )

    @property
    def coverage_ratio(self) -> float:

        total = (
            self.served_clients +
            self.unserved_clients
        )

        if total == 0:
            return 0.0

        return self.served_clients / total

    @property
    def average_route_distance(self) -> float:

        if not self.routes:
            return 0.0

        return (
            self.total_distance /
            len(self.routes)
        )

    def __repr__(self):

        return (
            f"Solution("
            f"algorithm='{self.algorithm}', "
            f"distance={self.total_distance:.2f}, "
            f"routes={self.route_count})"
        )