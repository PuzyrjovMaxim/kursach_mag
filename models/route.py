from dataclasses import dataclass, field

from models.client import Client


@dataclass
class Route:

    vehicle_id: int

    clients: list[Client] = field(
        default_factory=list
    )

    load: int = 0

    distance: float = 0.0

    total_time: float = 0.0

    feasible: bool = True

    def add_client(
        self,
        client: Client
    ):

        self.clients.append(client)

        self.load += client.demand

    @property
    def customer_count(self) -> int:

        return len(self.clients)

    @property
    def is_empty(self) -> bool:

        return len(self.clients) == 0

    def __len__(self):

        return len(self.clients)

    def __repr__(self):

        ids = [
            client.id
            for client in self.clients
        ]

        return (
            f"Route("
            f"vehicle={self.vehicle_id}, "
            f"clients={ids})"
        )