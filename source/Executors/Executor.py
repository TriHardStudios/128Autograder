import shutil
import os

from typing import List, Optional

from .Environment import ExecutionEnvironment, PossibleResults

from StudentSubmission.SubmissionProcessFactory import SubmissionProcessFactory

# For typing only
from StudentSubmission.Runners import IRunner
from StudentSubmission.ISubmissionProcess import ISubmissionProcess


class Executor:
    @classmethod
    def setup(cls, environment: ExecutionEnvironment, runner: IRunner) -> ISubmissionProcess:
        process = SubmissionProcessFactory.createProcess(environment, runner)

        if os.path.exists(environment.SANDBOX_LOCATION):
            shutil.rmtree(environment.SANDBOX_LOCATION)

        try:
            # create the sandbox and ensure that we have RWX permissions
            os.mkdir(environment.SANDBOX_LOCATION)
        except OSError as ex:
            raise EnvironmentError(f"Failed to create sandbox for test run. Error is: {ex}")

        if environment.files:
            for src, dest in environment.files.items():
                try:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy(src, dest)
                except OSError as ex:
                    raise EnvironmentError(f"Failed to move file '{src}' to '{dest}'. Error is: {ex}")

        return process
        
    @classmethod
    def execute(cls, environment: ExecutionEnvironment, runner: IRunner, raiseExceptions: bool = True) -> None:
        runner.setSubmission(environment.submission.getExecutableSubmission())

        submissionProcess: ISubmissionProcess = cls.setup(environment, runner)

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
            shutil.rmtree(environment.SANDBOX_LOCATION)


        

