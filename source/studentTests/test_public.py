from TestingFramework import BaseTest
from StudentSubmission import StudentSubmissionAssertions


class TestyTheTest(BaseTest, StudentSubmissionAssertions):

    def test_coolioboiio(self):
        self.assertEquals("Hello", "Goodbye")

    def test_neato(self):
        self.assertAlmostEquals(1.0, 1.0, _delta=0)
