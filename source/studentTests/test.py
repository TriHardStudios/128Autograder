from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from TestingFramework import BaseTest
from StudentSubmission import StudentSubmissionStdIOAssertions


class EmptyTestCase(BaseTest, StudentSubmissionStdIOAssertions):
    pass


