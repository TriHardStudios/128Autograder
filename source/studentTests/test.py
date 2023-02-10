from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from TestingFramework import BaseTest
from StudentSubmission import StudentSubmissionStdIOAssertions


class TestStdIO(BaseTest, StudentSubmissionStdIOAssertions):
    @weight(1.0)
    @number("1.0")
    @visibility("visible")
    def test_stdIO(self):
        """Simple IO Test"""


        expected: list[str] = [f"{int('10', 2)}", f"1000"]

        actual = []
        self.assertSubmissionExecution(self.studentSubmission, ["10"], actual, 10)

        self.assertOutputValid(expected, actual)

        self.assertEqual(self.reformatOutput(expected), self.reformatOutput(actual))
