from abc import ABC, abstractmethod

from models.instance import Instance


class BaseParser(ABC):

    @abstractmethod
    def parse(self, file_path: str) -> Instance:
        pass