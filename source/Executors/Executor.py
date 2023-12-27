import shutil
import os

from Executors.Environment import ExecutionEnvironment
from StudentSubmission import SubmissionProcessFactory

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
    def execute(cls, environment: ExecutionEnvironment, runner: IRunner) -> None:
        runner.setSubmission(environment.submission.getExecutableSubmission())

        submissionProcess: ISubmissionProcess = cls.setup(environment, runner)

        submissionProcess.run()

        cls.postRun(environment, submissionProcess)


    @classmethod
    def postRun(cls, environment: ExecutionEnvironment, submissionProcess: ISubmissionProcess) -> None:
        submissionProcess.cleanup()

        submissionProcess.populateResults(environment)

        # Might need to do some post processing of the results? 


    @classmethod
    def cleanup(cls, environment: ExecutionEnvironment):
        if os.path.exists(environment.SANDBOX_LOCATION):
            shutil.rmtree(environment.SANDBOX_LOCATION)


        

