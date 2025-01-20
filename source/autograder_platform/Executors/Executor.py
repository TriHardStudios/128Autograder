import shutil
import os
import sys

from autograder_platform.Executors.Environment import ExecutionEnvironment

from autograder_platform.StudentSubmission.SubmissionProcessFactory import SubmissionProcessFactory
from autograder_platform.Tasks.TaskRunner import TaskRunner
from autograder_platform.config.Config import AutograderConfigurationProvider, AutograderConfiguration

# For typing only
from autograder_platform.StudentSubmission.ISubmissionProcess import ISubmissionProcess


class Executor:
    @classmethod
    def setup(cls, environment: ExecutionEnvironment, runner: TaskRunner, autograderConfig: AutograderConfiguration) -> ISubmissionProcess:
        cls.cleanup(environment)

        # we are temporarily suppressing the errors with file creation should they occur.
        try:
            # create the sandbox and ensure that we have RWX permissions
            os.mkdir(environment.SANDBOX_LOCATION)
        except OSError as ex:  # pragma: no coverage
            # raise EnvironmentError(f"Failed to create sandbox for test run. Error is: {ex}")
            print(f"ERROR: Failed to create sandbox folder.\n{ex}", file=sys.stderr)  # pragma: no coverage

        # TODO Logging

        process = SubmissionProcessFactory.createProcess(environment, runner, autograderConfig)

        if environment.files:
            for src, dest in environment.files.items():
                try:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy(src, dest)
                except OSError as ex:  # pragma: no coverage
                    raise EnvironmentError(f"Failed to move file '{src}' to '{dest}'. Error is: {ex}")  # pragma: no coverage

        return process
        
    @classmethod
    def execute(cls, environment: ExecutionEnvironment, runner: TaskRunner, raiseExceptions: bool = True) -> None:
        submissionProcess: ISubmissionProcess = cls.setup(environment, runner, AutograderConfigurationProvider.get())

        submissionProcess.run()

        cls.postRun(environment, submissionProcess, raiseExceptions)

    @classmethod
    def postRun(cls, environment: ExecutionEnvironment, 
                submissionProcess: ISubmissionProcess, raiseExceptions: bool) -> None:

        submissionProcess.cleanup()

        submissionProcess.populateResults(environment)

        if raiseExceptions:
            # Moving this into the actual submission process allows for each process type to
            # handle their exceptions differently
            submissionProcess.processAndRaiseExceptions(environment)


    @classmethod
    def cleanup(cls, environment: ExecutionEnvironment):
        if os.path.exists(environment.SANDBOX_LOCATION):
            try:
                shutil.rmtree(environment.SANDBOX_LOCATION)
            except OSError as ex:  # pragma: no coverage
                print(f"ERROR: Failed to remove sandbox folder.\n{ex}", file=sys.stderr)  # pragma: no coverage
