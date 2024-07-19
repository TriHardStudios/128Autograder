import abc
from Executors.Environment import ExecutionEnvironment

from StudentSubmission.IRunner import IRunner


class ISubmissionProcess(abc.ABC):
    @abc.abstractmethod
    def setup(self, environment: ExecutionEnvironment, runner: IRunner):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def populateResults(self, environment: ExecutionEnvironment):
        pass

    @abc.abstractmethod
    def cleanup(self):
        pass

    @classmethod
    @abc.abstractmethod
    def processAndRaiseExceptions(cls, environment: ExecutionEnvironment):
        pass
