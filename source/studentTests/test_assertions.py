from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from TestingFramework import BaseTest
from StudentSubmission import StudentSubmissionStdIOAssertions


class TestAssertions(BaseTest, StudentSubmissionStdIOAssertions):

    def test_list(self):
        self.assertListEqual([1, 1.0, "hello!", None, False], "[1, 1.0, \"hello!\", None, False]")
        self.assertListEqual([1, 1.0, "hello!", None, False], [1, 1.0, "hello!", None, False])

    def test_tuple(self):
        self.assertTupleEqual((1, 2), (1, 2))
