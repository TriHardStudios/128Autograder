import shutil
import os

from typing import List, Optional

from StudentSubmission.SubmissionProcessFactory import SubmissionProcessFactory
from .Environment import ExecutionEnvironment, PossibleResults

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


    @staticmethod
    def _filterStdOut(stdout: List[str]) -> List[str]:
        """
        This function takes in a list representing the output from the program. It includes ALL output,
        so lines may appear as 'NUMBER> OUTPUT 3' where we only care about what is right after the OUTPUT statement
        This is adapted from John Henke's implementation

        :param _stdOut: The raw stdout from the program
        :returns: the same output with the garbage removed
        """

        filteredOutput: list[str] = []
        for line in stdout:
            if "output " in line.lower():
                filteredOutput.append(line[line.lower().find("output ") + 7:])

        return filteredOutput

    @staticmethod
    def _processException(exception: Exception) -> str:
        """
        This function formats the exception a more readable way. Should expand this.

        Rob said he wants:
        - line numbers (hard bc its a fake file)
        - Better support for runtime exceptions
        - the piece of code that actually caused the exception

        In theory, we could do this - it would require overriding the base exception class in the student's submission
        which is a pain to be honest.
        :param exception: The exception from the students submission
        :return: A nicely formatted message explaining the exception
        """
        errorMessage = f"Submission execution failed due to an {type(exception).__qualname__} exception.\n" + str(exception)

        if isinstance(exception, EOFError):
            errorMessage += "\n" \
                            "Are you missing if __name__ == '__main__'?\n" \
                            "Is your code inside of the branch?"

        return errorMessage

    @staticmethod
    def updateEnvironmentFileNames(files: dict[str, str]) -> dict[str, str]:
        updatedEnvironmentFiles = {}

        for _, value in files.items():
            updatedEnvironmentFiles[value] = value

        return updatedEnvironmentFiles

    @staticmethod
    def _resultPostProcessing(environment: ExecutionEnvironment):
        resultData = environment.resultData

        resultData[PossibleResults.STDOUT] = Executor._filterStdOut(resultData[PossibleResults.STDOUT])


        if environment.files is not None:
            # this approach means that nested fs changes aren't detected, but I don't see that coming up.

            curFiles = [file for file in os.listdir(environment.SANDBOX_LOCATION) if os.path.isfile(os.path.join(environment.SANDBOX_LOCATION, file))]

            # update files names to account for alaises

            environment.files = Executor.updateEnvironmentFileNames(environment.files)

            resultData[PossibleResults.FILE_OUT] = {}

            # We put them into a set and then eliminate the elements that are the same between the two sets
            diffFiles: list[str] = list(set(curFiles) ^ set(environment.files.keys()))

            for file in diffFiles:
                resultData[PossibleResults.FILE_OUT][file] = \
                    os.path.join(environment.SANDBOX_LOCATION, file)

        environment.resultData = resultData

        



    @classmethod
    def postRun(cls, environment: ExecutionEnvironment, 
                submissionProcess: ISubmissionProcess, raiseExceptions: bool) -> None:

        submissionProcess.cleanup()

        submissionProcess.populateResults(environment)

        cls._resultPostProcessing(environment)

        if raiseExceptions:
            exception: Optional[Exception] =\
                environment.resultData[PossibleResults.EXCEPTION] \
                if PossibleResults.EXCEPTION in environment.resultData else None

            if exception is not None:
                raise AssertionError(cls._processException(exception))

        # Might need to do some post processing of the results? 



    @classmethod
    def cleanup(cls, environment: ExecutionEnvironment):
        if os.path.exists(environment.SANDBOX_LOCATION):
            shutil.rmtree(environment.SANDBOX_LOCATION)


        

