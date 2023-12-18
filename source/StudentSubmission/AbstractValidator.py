import abc
from typing import List

class ValidationError(Exception):
    pass

class AbstractValidator(abc.ABCMeta):
    def __init__(self):
        self.validationErrors: List[ValidationError] = []

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    def collectErrors(self) -> List[ValidationError]:
        return self.validationErrors
