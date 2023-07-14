from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from TestingFramework import BaseTest
from StudentSubmission import StudentSubmissionAssertions
from StudentSubmission.StudentSubmissionExecutor import StudentSubmissionExecutor
from StudentSubmission.Runners import MainModuleRunner
from StudentSubmission.common import PossibleResults


class HelloWorld(BaseTest, StudentSubmissionAssertions):

    @weight(10)
    def testCode(self):
        environment = StudentSubmissionExecutor.generateNewExecutionEnvironment(self.studentSubmission)
        runner = MainModuleRunner()

        StudentSubmissionExecutor.execute(environment, runner)

        actualOutput = StudentSubmissionExecutor.getOrAssert(PossibleResults.STDOUT)
        self.assertEqual("Hello World", actualOutput[0])
