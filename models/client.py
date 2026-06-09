from dataclasses import dataclass


@dataclass(slots=True)
class Client:
    """
    Узел задачи CVRPTW.

    Для Solomon:
        id = 0  -> depot
        id > 0  -> customer
    """

    id: int

    x: float
    y: float

    demand: int

    ready_time: float
    due_date: float

    service_time: float

    @property
    def is_depot(self) -> bool:
        return self.id == 0

    def __repr__(self) -> str:
        return (
            f"Client("
            f"id={self.id}, "
            f"demand={self.demand})"
        )