from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from TestingFramework import BaseTest
from StudentSubmission import StudentSubmissionAssertions
from StudentSubmission.StudentSubmissionExecutor import StudentSubmissionExecutor
from StudentSubmission.Runners import MainModuleRunner
from StudentSubmission.common import PossibleResults


class TestStdIO(BaseTest, StudentSubmissionAssertions):

    def setUp(self):
        self.environment = StudentSubmissionExecutor.generateNewExecutionEnvironment(self.studentSubmission)
        self.runner = MainModuleRunner()

    def tearDown(self):
        StudentSubmissionExecutor.cleanup(self.environment)

    def runStdIOTest(self, _input, _expectedOutput):
        actual: list[str] = []
        self.environment.stdin = _input

        StudentSubmissionExecutor.execute(self.environment, self.runner)

        actual = StudentSubmissionExecutor.getOrAssert(PossibleResults.STDOUT)

        self.assertCorrectNumberOfOutputLines(_expectedOutput, actual)


        self.assertEqual(self.reformatOutput(_expectedOutput), self.reformatOutput(actual))

    @weight(1.0)
    @number(1.1)
    def test_addition(self):
        """Simple Integer Addition Test"""

        expected: list[str] = [f"{2 + 2}"]
        input: list[str] = ["1", "2", "2"]

        self.runStdIOTest(input, expected)

    @weight(1.0)
    @number(1.2)
    def test_subtraction(self):
        """Simple Integer Subtraction Test"""

        expected: list[str] = [f"{2 - 2}"]
        input: list[str] = ["2", "2", "2"]

        self.runStdIOTest(input, expected)

    @weight(1.0)
    @number(1.3)
    def test_multiplation(self):
        """Simple Integer Multiplcation Test"""

        expected: list[str] = [f"{2 * 2}"]
        input: list[str] = ["3", "2", "2"]

        self.runStdIOTest(input, expected)

    @weight(1.0)
    @number(1.5)
    def test_multiplation(self):
        """Simple Float Division Test"""

        expected: list[str] = [f"{2 / 2:.02f}"]
        input: list[str] = ["5", "2", "2"]

        self.runStdIOTest(input, expected)

    @weight(1.0)
    @number(1.4)
    def test_division(self):
        """Simple Integer Division Test"""

        expected: list[str] = [f"{2 // 2}"]
        input: list[str] = ["4", "2", "2"]

        self.runStdIOTest(input, expected)

    @weight(1.0)
    @number(2.1)
    def test_floatAddition(self):
        """Float Addition Test"""
        expected: list[str] = [f"{1.5 + 2:.0f}"]
        input: list[str] = ["1", "1.5", "2"]

        self.runStdIOTest(input, expected)

    @weight(1.0)
    @number(2.2)
    def test_intDivisionWithFloats(self):
        """Integer Division with Floats"""
        expected: list[str] = [f"{10.5 // 3.1:.0f}"]
        input: list[str] = ["4", "10.5", "3.1"]

        self.runStdIOTest(input, expected)

    @weight(1.0)
    @number(2.3)
    def test_floatDivision(self):
        """Float Division Test"""
        expected: list[str] = [f"{10 / 3:.02f}"]
        input: list[str] = ["5", "10", "3"]

        self.runStdIOTest(input, expected)
