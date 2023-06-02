from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from TestingFramework import BaseTest
from StudentSubmission import StudentSubmissionAssertions
from StudentSubmission.StudentSubmissionExecutor import StudentSubmissionExecutor
from StudentSubmission.Runners import MainModuleRunner
from StudentSubmission.common import PossibleResults

class EmptyTestSuite(BaseTest, StudentSubmissionAssertions):
    pass
