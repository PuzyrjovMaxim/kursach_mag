from abc import ABC
from abc import abstractmethod


class BaseSolver(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def solve(
        self,
        instance
    ):
        pass

    def __str__(
        self
    ):

        return self.name

    def __repr__(
        self
    ):

        return self.name