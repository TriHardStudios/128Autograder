import abc
from typing import List

class AbstractValidator(abc.ABC):
    def __init__(self):
        self.errors: List[Exception] = []

    @abc.abstractmethod
    # this should be typed, but its a weird cross depenacny issue
    def setup(self, studentSubmission):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    def collectErrors(self) -> List[Exception]:
        return self.errors
