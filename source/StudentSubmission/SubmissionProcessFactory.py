from typing import Dict, Type

from Executors.Environment import ExecutionEnvironment
from .Runners import IRunner

from .AbstractStudentSubmission import AbstractStudentSubmission
from .ISubmissionProcess import ISubmissionProcess


class SubmissionProcessFactory():
    registry: Dict[Type[AbstractStudentSubmission], Type[ISubmissionProcess]] = {}


    @classmethod
    def register(cls, submission: Type[AbstractStudentSubmission], process: Type[ISubmissionProcess]) -> None:
        if not issubclass(process, ISubmissionProcess):
            raise TypeError(f"{process} is not a subclass of ISubmissionProcess! Registration failed!")

        if not issubclass(submission, AbstractStudentSubmission):
            raise TypeError(f"{submission} is not a subclass of AbstractStudentSubmission! Registration failed!")

        # TODO Add logging here
        cls.registry[submission] = process

    @classmethod
    def createProcess(cls, environment: ExecutionEnvironment, runner: IRunner) -> ISubmissionProcess:
        submissionType = type(environment.submission)

        if submissionType not in cls.registry.keys():
            raise TypeError(f"{submissionType} has not been registered. Lookup failed.")

        process = cls.registry[submissionType]()

        process.setup(environment, runner)

        return process
