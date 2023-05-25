import abc
from enum import Enum


class PossibleResults(Enum):
    STDOUT = "stdout"
    RETURN_VAL = "return_val"
    FILE_OUT = "file_out"
    MOCK_SIDE_EFFECTS = "mock"


class Runner:
    def __init__(self):
        pass

    @abc.abstractmethod
    def __call__(self):
        raise NotImplementedError("Must use implementation of runner.")
