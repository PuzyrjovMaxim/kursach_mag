from dataclasses import dataclass
from dataclasses import field

from models.client import Client


@dataclass
class Instance:

    name: str

    vehicle_count: int

    vehicle_capacity: int

    nodes: list[Client]

    distance_matrix: object | None = None

    _node_map: dict[int, Client] = field(
        init=False,
        repr=False
    )

    def __post_init__(self):

        self._node_map = {
            node.id: node
            for node in self.nodes
        }

    @property
    def depot(self) -> Client:

        return self.nodes[0]

    @property
    def clients(self) -> list[Client]:

        return self.nodes[1:]

    @property
    def customer_count(self) -> int:

        return len(self.nodes) - 1

    @property
    def total_demand(self) -> int:

        return sum(
            client.demand
            for client in self.clients
        )

    def get_node(
        self,
        node_id: int
    ) -> Client:

        return self._node_map[node_id]

    def __repr__(self):

        return (
            f"Instance("
            f"name='{self.name}', "
            f"customers={self.customer_count}, "
            f"vehicles={self.vehicle_count}, "
            f"capacity={self.vehicle_capacity})"
        )