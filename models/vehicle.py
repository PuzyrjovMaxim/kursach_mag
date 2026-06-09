from dataclasses import dataclass


@dataclass(slots=True)
class Vehicle:

    id: int

    capacity: int

    def __repr__(self) -> str:
        return (
            f"Vehicle("
            f"id={self.id}, "
            f"capacity={self.capacity})"
        )