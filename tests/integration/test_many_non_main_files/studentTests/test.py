import unittest
from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from Executors.Executor import Executor
from StudentSubmissionImpl.Python.PythonSubmission import PythonSubmission
from StudentSubmission.Runners import MainModuleRunner


class HelloWorld(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.studentSubmission = PythonSubmission()\
                .setSubmissionRoot(cls.submissionDirectory)\
                .load()\
                .build()

    @unittest.skip("Dear jesus if this gets printed ill be very impressed")
    @weight(10)
    def testCode(self):
        environment = StudentSubmissionExecutor.generateNewExecutionEnvironment(self.studentSubmission)
        runner = MainModuleRunner()

        StudentSubmissionExecutor.execute(environment, runner)

        actualOutput = StudentSubmissionExecutor.getOrAssert(environment, PossibleResults.STDOUT)
        self.assertEqual("Hello World", actualOutput[0])
