from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from TestingFramework import BaseTest
from StudentSubmission import StudentSubmissionAssertions


class EmptyTestCase(BaseTest, StudentSubmissionAssertions):
    pass


