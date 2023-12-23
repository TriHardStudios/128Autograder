from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from TestingFramework import BaseTest
from StudentSubmission.StudentSubmissionExecutor import StudentSubmissionExecutor
from StudentSubmission.Runners import FunctionRunner
from StudentSubmission.common import PossibleResults


class HelloWorld(BaseTest):

    @weight(10)
    def testCode(self):
        environment = StudentSubmissionExecutor.generateNewExecutionEnvironment(self.studentSubmission)
        runner = FunctionRunner("hello_world")

        StudentSubmissionExecutor.execute(environment, runner)

        actualOutput = StudentSubmissionExecutor.getOrAssert(environment, PossibleResults.STDOUT)
        self.assertEqual("Hello World", actualOutput[0])
