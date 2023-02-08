import unittest
from unittest.mock import patch

from gradescope_utils.autograder_utils.decorators import weight, visibility, number

from io import StringIO

from StudentSubmission import StudentSubmission
from StudentSubmissionStdIOAssertions import StudentSubmissionStdIOAssertions


class Test(unittest.TestCase, StudentSubmissionStdIOAssertions):
    studentSubmission: StudentSubmission | None = None

    @classmethod
    def setUpClass(cls):
        cls.studentSubmission = StudentSubmission("/autograder/submission/", ["eval()", "int(_, 16)"])
        cls.studentSubmission.validateSubmission()

    @classmethod
    def reformatOuput(cls, _output: list[str]) -> str:
        return "".join("OUTPUT " + line + "\n" for line in _output)

    @classmethod
    def tearDownClass(cls):
        pass

    def failIfInvalid(self):
        self.assertTrue(self.studentSubmission.isSubmissionValid(),
                        msg=f"Student submission is invalid due to:\n{self.studentSubmission.getValidationError()}")

    def failIfNotModule(self):
        pass

    @weight(1.0)
    @number("1.0")
    @visibility("visible")
    def test_sanityCheck(self):
        """Simple IO Test"""
        self.failIfInvalid()
        expected: list[str] = [f"{int('10', 2)}", f"1000"]

        # completedSuccessfully, actual = self.studentSubmission.runMainModule(["10"], 10)
        actual = []
        self.assertSubmissionExecution(self.studentSubmission, ["10"], actual, 10)

        # self.assertTrue(completedSuccessfully, msg=f"Failed to execute student submission. Error: {actual[0]}")

        self.assertGreater(len(actual), 0, msg="No OUTPUT lines.\nCheck output formatting")

        self.assertEqual(len(expected), len(actual), msg="Incorrect number of OUTPUT lines.\nCheck output formatting")

        self.assertEqual(self.reformatOuput(expected), self.reformatOuput(actual))
