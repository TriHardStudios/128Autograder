import os
from typing import List, Dict, TypeVar, Union

import dataclasses
from StudentSubmission import AbstractStudentSubmission
from StudentSubmission.common import PossibleResults

@dataclasses.dataclass
class ExecutionEnvironment:
    """
    Description
    ===========

    This class defines the execution environment for the student's submission. It controls what data
    is provided and what 'pre-run' tasks are completed (ie: creating a class instance).
    This class does not define the actual executor.
    """

    submission: AbstractStudentSubmission
    """The student submission that will be executed"""
    stdin: List[str] = dataclasses.field(default_factory=list)
    """If stdin will be passed to the student's submission"""
    files: Dict[str, str] = dataclasses.field(default_factory=dict)
    """What files need to be added to the students submission. 
    The key is the file name, and the value is the file name with its relative path"""
    mocks: Dict[str, object] = dataclasses.field(default_factory=dict)
    """What mocks have been defined for this run of the student's submission"""
    timeout: int = 10
    """What timeout has been defined for this run of the student's submission"""

    resultData: dict[PossibleResults, object] = dataclasses.field(default_factory=dict)
    """
    This dict contains the data that was generated from the student's submission. This should not be accessed
    directly, rather, use getOrAssert method
    """

    SANDBOX_LOCATION: str = "./sandbox"

Builder = TypeVar("Builder", bound="ExecutionEnvironmentBuilder")

class ExecutionEnvironmentBuilder():
    """
    Description
    ===========

    This class helps build the execution environments.

    See :ref:`ExecutionEnvironment` for more information
    """

    def __init__(self, submission: AbstractStudentSubmission):
        self.environment = ExecutionEnvironment(submission)
        self.dataRoot = "."

    def setDataRoot(self: Builder, dataRoot: str) -> Builder:
        """
        Description
        ---
        This function sets the data root for the execution environment, 
        meaning what prefix should be added to all the files supplied to executor

        IE: if we had a file at ``tests/data/public/file.txt``, data root should be set to 
        ``tests/data`` or ``tests/data/public``

        :param dataRoot: the data root to use.
        """
        self.dataRoot = dataRoot

        return self

    def setStdin(self: Builder, stdin: Union[List[str], str]) -> Builder:
        """
        Description
        ---
        This function sets the STDIN to supply to the student's submission.

        This should be set to the number of input lines that the submission should use.

        If stdin is supplied as a string, it will be turned into a list seperated by newlines.

        :param stdin: Either a list of input strings or a string seperated by newlines (``\n``).
        """
        if isinstance(stdin, str):
            stdin = stdin.splitlines()

        self.environment.stdin = stdin

        return self


    def addMock(self: Builder, mockName: str, mockObject: object) -> Builder:
        """
        This needs to be updated once we decide how to do mocks
        """
        self.environment.mocks[mockName] = mockObject

        return self

    def addFile(self: Builder, fileSrc: str, fileDest: str) -> Builder:
        """
        Description
        ---
        This function adds a file to be pulled into the environment.

        :param fileSrc: The path to the file, relative to the specified data root. 
        IE: if we had a file at ``tests/data/public/file.txt``, and data root was set to ``tests/data``, 
        then ``fileSrc`` should be ``./public/file.txt``.
        :param fileDest: The path relative to ``SANDBOX_LOCATION`` that the file should be dropped at.
        """
        fileSrc = os.path.join(self.dataRoot, fileSrc)
        fileDest = os.path.join(self.environment.SANDBOX_LOCATION, fileDest)

        self.environment.files[fileSrc] = fileDest

        return self


    def setTimeout(self: Builder, timeout: int) -> Builder:
        """
        Description
        ---
        This function sets the timeout to kill the student's submission in if it doesn't end before that.

        The timeout must be integer greater than 1.

        :param timeout: The timeout to use.
        """
        if not isinstance(timeout, int):
            raise AttributeError(f"Timeout MUST be an integer. Was {type(timeout).__qualname__}")

        if timeout < 1:
            raise AttributeError(f"Timeout MUST be greater than 1. Was {timeout}")

        self.environment.timeout = timeout

        return self


    @staticmethod
    def _validate(environment: ExecutionEnvironment):
        # For now this only validating that the files actually exist

        for src in environment.files.keys():
            if not os.path.exists(src):
                raise EnvironmentError(f"File {src} does not exist or is not accessible!")

        # TODO - Validate requested features

    def build(self) -> ExecutionEnvironment:
        """
        Description
        ---
        This function validates that the execution environment is valid and then returns the environment.

        :returns: The build environment
        """
        self._validate(self.environment)

        return self.environment
