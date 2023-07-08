import sys
import unittest

from StudentSubmission import StudentSubmission
from StudentSubmission import StudentSubmissionAssertions
from .Assertions import Assertions


class BaseTest(Assertions, StudentSubmissionAssertions):
    studentSubmission: StudentSubmission | None = None
    submissionDirectory: str | None = None

    @classmethod
    def setUpClass(cls):
        cls.studentSubmission = StudentSubmission(cls.submissionDirectory, ["eval()"])
        cls.studentSubmission.validateSubmission()
        cls.studentSubmission.installRequirements()

    @classmethod
    def reformatOutput(cls, _output: list[str]) -> str:
        return "".join("OUTPUT " + line + "\n" for line in _output)

    @classmethod
    def tearDownClass(cls):
        cls.studentSubmission.removeRequirements()
