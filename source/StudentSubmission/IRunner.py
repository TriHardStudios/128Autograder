from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Tuple, Any, List

T = TypeVar('T')

class IRunner(ABC):
    """

    """
    @abstractmethod
    def __init__(self, tasks: List[Task]):  # ignore: unused
        raise NotImplementedError()

    @abstractmethod
    def run(self) -> T:
        raise NotImplementedError()

