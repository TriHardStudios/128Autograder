from abc import ABC, abstractmethod
from typing import Generic, TypeVar
T_code = TypeVar("T_code")

class IRunner(ABC, Generic[T_code]):
    @abstractmethod
    def setSubmission(self, submission: T_code): 
        raise NotImplementedError()
