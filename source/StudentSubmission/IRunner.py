from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Tuple, Any
T = TypeVar('T')

class IRunner(ABC):
    """

    """
    @abstractmethod
    def run(self) -> T:
        raise NotImplementedError()

