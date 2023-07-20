"""
This file provides the executor for the student submissions.

The executor is responsible for setting up and tearing down the execution environment, running the submission, and
providing an interface for reading the artifacts from a student submission.

This allows the execution environment to be a lot more flexible in terms of what can actually be tested, and with the
generic runner class, a great deal of flexibility is afforded to the unit test authors.

This class also means that less work is needed ot actually write unit tests and less custom assertions need to be used,
which is nice.

:author: Gregory Bell
:date: 6/24/23
"""

import dataclasses
import multiprocessing
import os.path
import shutil
import unittest.mock

import dill

from StudentSubmission import RunnableStudentSubmission
from StudentSubmission import StudentSubmission
from StudentSubmission.common import PossibleResults, filterStdOut
from StudentSubmission.Runners import Runner

# We need to use the dill pickle-ing library to pass functions in the processes
dill.Pickler.dumps, dill.Pickler.loads = dill.dumps, dill.loads
multiprocessing.reduction.dump = dill.dump


class StudentSubmissionExecutor:
    dataDirectory: str | None = None
    """The directory where all the data for tests lives"""



    @dataclasses.dataclass
    class ExecutionEnvironment:
        """
        :Description:
            This class defines the execution environment for the student's submission. It controls what data
            is provided and what 'pre-run' tasks are completed (ie: creating a class instance).
            This class does not define the actual executor.
        """

        submission: StudentSubmission
        """The student submission that will be executed"""
        stdin: list[str] | str = ""
        """If stdin will be passed to the student's submission"""
        files: dict[str, str] | None = None
        """What files need to be added to the students submission. 
        The key is the file name, and the value is the file name with its relative path"""
        mocks: dict[str, unittest.mock.Mock] | None = None
        """What mocks have been defined for this run of the student's submission"""
        timeout: int = 10
        """What _timeout has been defined for this run of the student's submission"""

        resultData: dict[PossibleResults, any] = dataclasses.field(default_factory=dict)
        """
        This dict contains the data that was generated from the student's submission. This should not be accessed
        directly, rather, use getOrAssert method
        """

        SANDBOX_LOCATION: str = "./sandbox"

    @staticmethod
    def generateNewExecutionEnvironment(_submission: StudentSubmission) -> ExecutionEnvironment:
        """
        :Description:
            This function generates a new execution environment with the student's submission. If it is not possible
            due to a validation error, then the assertion error will be thrown.

            It is up to the actual unit test user to populate the environment
        :param _submission: the student submission to use in the environment
        :return: the execution environment that needs to be populated by the user
        :raises AssertionError: if the submission is not valid
        """
        if not _submission.isSubmissionValid():
            raise AssertionError(_submission.getValidationError())

        return StudentSubmissionExecutor.ExecutionEnvironment(_submission)

    @classmethod
    def _getUpdatedFilePaths(cls, _environment: ExecutionEnvironment) -> dict[os.PathLike, os.PathLike]:

        filesToMove = _environment.files
        if filesToMove is not None:
            filesToMove = dict(zip(
                [os.path.join(cls.dataDirectory, srcFile) for srcFile in filesToMove.keys()],
                [os.path.join(_environment.SANDBOX_LOCATION, destFile) for destFile in filesToMove.values()]
            ))

        # add imported files if they exist
        importedFiles = _environment.submission.getImports()
        if importedFiles:
            importedFiles = dict(zip(
                [srcFile for srcFile in importedFiles.keys()],
                [os.path.join(_environment.SANDBOX_LOCATION, destFile) for destFile in importedFiles.values()]
            ))

            if filesToMove is not None:
                filesToMove.update(importedFiles)
            else:
                filesToMove = importedFiles

        return filesToMove

    @classmethod
    def setup(cls, _environment: ExecutionEnvironment, _runner: Runner) -> RunnableStudentSubmission:
        """
        This function sets up the environment to run the submission in. It pulls in all the files that are requested
        and preps the mocks to be passed into the actual process.
        :param _environment: the execution environment to execute the submission in.
        :param _runner: the runner that contains the student's code

        :return: This function returns the runnable student submission that can be executed
        :raise EnvironmentError: This function will raise a non-assertion error in the event that any of the setup fails.
        """

        if not os.path.exists(_environment.SANDBOX_LOCATION):
            try:
                # create the sandbox and ensure that we have RWX permissions
                os.mkdir(_environment.SANDBOX_LOCATION)
            except OSError as os_ex:
                raise EnvironmentError(f"Failed to create sandbox for test run. Error is: {os_ex}")

        filesToMove = cls._getUpdatedFilePaths(_environment)

        if filesToMove:
            # this moves all required files over to the sandbox for testing
            for srcPath, destPath in filesToMove.items():
                if not os.path.exists(srcPath):
                    raise EnvironmentError(
                        f"Failed to locate file: '{srcPath}'. '{srcPath}' is required for this environment."
                    )
                if not os.path.exists(os.path.dirname(destPath)):
                    # This is not super likely to throw an error bc we already created the folder above
                    os.mkdir(os.path.dirname(destPath))

                shutil.copyfile(srcPath, destPath)

        runnableSubmission: RunnableStudentSubmission = RunnableStudentSubmission.RunnableStudentSubmission(
            _environment.stdin, _runner,
            _environment.SANDBOX_LOCATION,
            _environment.timeout)

        return runnableSubmission

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
        return f"Submission execution failed due to an {type(exception).__qualname__} exception."

    @classmethod
    def execute(cls, _environment: ExecutionEnvironment, _runner: Runner) -> None:
        _runner.setSubmission(_environment.submission.getStudentSubmissionCode())
        runnableSubmission: RunnableStudentSubmission = cls.setup(_environment, _runner)
        runnableSubmission.run()

        # Doing this, this way is *much* better than re throwing the exceptions. It also gets rid of the need
        #  for more custom exceptions
        # If exceptions were raised then we need to process them
        if runnableSubmission.getException():
            raise AssertionError(cls._processException(runnableSubmission.getException()))

        if runnableSubmission.getTimeoutOccurred():
            raise AssertionError(f"Submission timed out after {_environment.timeout} seconds.")

        cls.postRun(_environment, runnableSubmission)

    @classmethod
    def postRun(cls, _environment: ExecutionEnvironment, _runnableSubmission: RunnableStudentSubmission) -> None:
        """
        This function runs the post-processing needed before we can deliver the results to the unittest.
        For now, it strips the output statements from STDOUT (if present), generates the valid files based on
        the FS diff before and after the runs
        :param _environment: the execution environment
        :param _runnableSubmission: the students submission that we need to gather data from
        """
        resultData = _runnableSubmission.getOutputData()

        if PossibleResults.STDOUT in resultData.keys():
            resultData[PossibleResults.STDOUT] = filterStdOut(resultData[PossibleResults.STDOUT])

        if _environment.files is not None:
            # this approach means that nested fs changes aren't detected, but I don't see that coming up.
            curFiles = os.listdir(_environment.SANDBOX_LOCATION)

            resultData[PossibleResults.FILE_OUT] = {}

            # We put them into a set and then eliminate the elements that are the same between the two sets
            diffFiles: list[str] = list(set(curFiles) ^ set(_environment.files.keys()))

            for file in diffFiles:
                resultData[PossibleResults.FILE_OUT][file] = \
                    os.path.join(_environment.SANDBOX_LOCATION, file)

        _environment.resultData = resultData

    @classmethod
    def getOrAssert(cls, _environment: ExecutionEnvironment,
                    _field: PossibleResults,
                    file: str | None = None,
                    mock: str | None = None) -> any:
        """
        This function gets the requested field from the results or will raise an assertion error.

        If a file is requested, the file name must be specified with the ``file`` parameter. The contents of the file
        will be returned.
        If a mock is requested, the mocked method's name must `also` be requested. The mocked method will be returned.
        :param _environment: the execution environment that contains the results from execution
        :param _field: the field to get data from in the results file. Must be a ``PossibleResult``
        :param file: if ``PossibleResults.FILE_OUT`` is specified, ``file`` must also be specified. This is the file
        name to load from.
        :param mock: if ``PossibleResults.MOCK_SIDE_EFFECT`` is specified, ``mock`` must also be specified. This is the
        mocked method name (usually from ``method.__name__``)

        :return: The requested data if it exists
        :raises AssertionError: if the data cannot be retrieved for whatever reason
        """
        resultData = _environment.resultData

        if _field not in resultData.keys():
            raise AssertionError(f"Missing result data. Expected: {_field.value}.")

        if _field is PossibleResults.STDOUT and not resultData[_field]:
            raise AssertionError(f"No OUTPUT was created by the students submission.\n"
                                 f"Are you missing an 'OUTPUT' statement?")

        if _field is PossibleResults.FILE_OUT and not file:
            raise AttributeError("File must be defined.")

        if _field is PossibleResults.FILE_OUT and file not in resultData[PossibleResults.FILE_OUT].keys():
            raise AssertionError(f"File '{file}' was not created by the student's submission")

        if _field is PossibleResults.MOCK_SIDE_EFFECTS and not mock:
            raise AttributeError("Mock most be defined.")

        if _field is PossibleResults.MOCK_SIDE_EFFECTS \
                and mock not in resultData[PossibleResults.MOCK_SIDE_EFFECTS].keys():
            raise AttributeError(
                f"Mock '{mock}' was not returned by the student submission. This is an autograder error.")

        # now that all that validation is done, we can actually give the data requested lol

        if _field is PossibleResults.FILE_OUT:
            # load the file from disk and return it
            return open(resultData[_field][file], 'r').read()

        if _field is PossibleResults.MOCK_SIDE_EFFECTS:
            return resultData[_field][mock]

        return resultData[_field]

    @classmethod
    def cleanup(cls, _environment: ExecutionEnvironment) -> None:
        """
        This function cleans out any persistent data between tests. There should be *very* little in
        this function as very little should be persisted. This function should only be called in the after
        each function
        """

        cls.resultData = {}

        shutil.rmtree(_environment.SANDBOX_LOCATION)
