import os
from io import StringIO

from .StudentSubmission import StudentSubmission


class StudentSubmissionAssertions:
    @staticmethod
    def assertSubmissionValid(_studentSubmission: StudentSubmission):
        if not _studentSubmission.isSubmissionValid():
            raise AssertionError(_studentSubmission.getValidationError())

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
