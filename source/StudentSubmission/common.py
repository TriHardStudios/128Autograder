from abc import ABC, abstractmethod
from enum import Enum


class PossibleResults(Enum):
    STDOUT = "stdout"
    RETURN_VAL = "return_val"
    FILE_OUT = "file_out"
    MOCK_SIDE_EFFECTS = "mock"


class Runner(ABC):
    def __init__(self):
        self.studentSubmissionCode = None

    def setSubmission(self):
        pass

    def setMocks(self):
        pass

    @abstractmethod
    def run(self):
        raise NotImplementedError("Must use implementation of runner.")

    def __call__(self):
        pass
