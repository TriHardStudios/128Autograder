import os
from io import StringIO

from .StudentSubmission import StudentSubmission


class StudentSubmissionAssertions:
    @staticmethod
    def assertSubmissionValid(_studentSubmission: StudentSubmission):
        if not _studentSubmission.isSubmissionValid():
            raise AssertionError(_studentSubmission.getValidationError())

    class StdIOAssertions:

        @staticmethod
        def assertSubmissionExecution(_studentSubmission: StudentSubmission,
                                      _stdin: list[str], _stdout: list[str],
                                      _timeout: int):

            status, stdout = _studentSubmission.runMainModule(_stdin, _timeout)

            if not status:
                stdout = [error for error in stdout if 'output' not in error.lower()]
                msg: str = "Failed to execute student submission."

                if stdout:
                    msg += " Error(s):\n"
                    for error in stdout:
                        msg += error + "\n"

                raise AssertionError(msg)

            _stdout.extend(stdout)

        @staticmethod
        def assertCorrectNumberOfOutputLines(expected: list[str], actual: list[str]):
            if len(actual) == 0:
                raise AssertionError("No OUTPUT lines found. Check OUTPUT formatting.")

            if len(actual) > len(expected):
                raise AssertionError(f"Too many OUTPUT lines. Check OUTPUT formatting.\n"
                                     f"Expected number of lines: {len(expected)}\n"
                                     f"Actual number of lines  : {len(actual)}")

            if len(actual) < len(expected):
                raise AssertionError(f"Too few OUTPUT lines. Check OUTPUT formatting.\n"
                                     f"Expected number of lines: {len(expected)}\n"
                                     f"Actual number of lines  : {len(actual)}")

    class FileIOAssertions:
        dataFileSource: str = "./data/"

        @staticmethod
        def readFromFile(_fileName: str) -> StringIO:
            if not os.path.exists(_fileName):
                raise AssertionError(f"File '{_fileName}' does not exist")

            fileContents = open(_fileName, 'r').readline()

            return StringIO(fileContents)

        @staticmethod
        def readFromArray(_stdin: list[str]) -> StringIO:
            combinedInput = "".join([el + '\n' for el in _stdin])

            return StringIO(combinedInput)

        @staticmethod
        def assertSubmissionExecution(_studentSubmission: StudentSubmission, _input: StringIO,
                                      _expected: StringIO, _actualFile: str, _timeout: int):
            pass

        @staticmethod
        def assertFileOutput(_expectedOutput: StringIO, _actualOutput: StringIO):
            pass
