import abc
from typing import Generic, TypeVar

from Executors.Environment import ExecutionEnvironment
from StudentSubmission.Runners import IRunner

T = TypeVar("T")
G = TypeVar("G")

class Executor(abc.ABC, Generic[T, G]):
    @classmethod
    @abc.abstractmethod
    def setup(cls, environment: ExecutionEnvironment, runner: IRunner) -> T:
        raise NotImplemented()

    @classmethod
    def execute(cls, environment: ExecutionEnvironment, runner: IRunner) -> None:
        runner.setSubmission(environment.submission.getExecutableSubmission())

        submissionProcess: T = cls.setup(environment, runner)


        

