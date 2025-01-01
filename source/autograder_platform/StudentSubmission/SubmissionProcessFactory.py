from typing import Dict, Type, Tuple, Optional, Callable

from lib.Executors.Environment import ExecutionEnvironment, ImplEnvironment, ImplResults

from lib.StudentSubmission.ISubmissionProcess import ISubmissionProcess

from lib.StudentSubmission.AbstractStudentSubmission import AbstractStudentSubmission
from lib.Tasks.TaskRunner import TaskRunner
from lib.config.Config import AutograderConfiguration


class SubmissionProcessFactory:
    registry: \
        Dict[Type[AbstractStudentSubmission],
        Tuple[Type[ISubmissionProcess],
        Optional[Type[ImplEnvironment]],
        Optional[Callable[[ImplEnvironment, AutograderConfiguration], None]]]] \
        = {}

    @classmethod
    def register(cls, submission: Type[AbstractStudentSubmission], process: Type[ISubmissionProcess],
                 implEnvironment: Optional[Type[ImplEnvironment]] = None,
                 implEnvironmentConfigMapper: Optional[
                     Callable[[ImplEnvironment, AutograderConfiguration], None]] = None) -> None:

        if submission in cls.registry:
            return

        if not issubclass(process, ISubmissionProcess):
            raise AttributeError(f"{process} is not a subclass of ISubmissionProcess! Registration failed!")

        if not issubclass(submission, AbstractStudentSubmission):
            raise AttributeError(f"{submission} is not a subclass of AbstractStudentSubmission! Registration failed!")

        if implEnvironment is not None and implEnvironmentConfigMapper is None:
            raise AttributeError(
                f"Implementation environment is provided for submission type {submission}, but no mapper is defined! Registration Failed!")

        if implEnvironment is None and implEnvironmentConfigMapper is not None:
            raise AttributeError(
                f"Implementation environment mapper is provided for submission type {submission}, but no implementation environment is defined! Registration Failed!")

        # TODO Add logging here
        cls.registry[submission] = (process, implEnvironment, implEnvironmentConfigMapper)

    @classmethod
    def createProcess(cls, environment: ExecutionEnvironment[ImplEnvironment, ImplResults],
                      runner: TaskRunner, autograderConfig: AutograderConfiguration) -> ISubmissionProcess:
        submissionType = runner.getSubmissionType()

        if submissionType not in cls.registry.keys():
            raise AttributeError(f"{submissionType} has not been registered. Lookup failed.")

        processType, implEnvironmentType, mapper = cls.registry[submissionType]

        if implEnvironmentType is not None and mapper is not None:
            if environment.impl_environment is None:
                environment.impl_environment = implEnvironmentType()

            mapper(environment.impl_environment, autograderConfig)

        process = processType()

        process.setup(environment, runner)

        return process