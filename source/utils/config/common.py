from typing import Dict, Generic, List, TypeVar
from abc import ABC, abstractmethod, abstractproperty

T = TypeVar("T")

class BaseSchema(Generic[T], ABC):

    @abstractmethod
    def validate(self, data: Dict) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def build(self, data: Dict) -> T:
        raise NotImplementedError()

