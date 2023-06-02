import unittest

from TestingFramework.Assertions import Assertions

class TestAssertions(Assertions):

    def testList(self):
        self.assertListEqual([1, 1.0, "hello!", None, False], "[1, 1.0, \"hello!\", None, False]")
        self.assertListEqual([1, 1.0, "hello!", None, False], [1, 1.0, "hello!", None, False])

    @unittest.expectedFailure
    def testListFailure1(self):
        self.assertListEqual([2, 3.0, "Hello!", None, False], [2, 3.0, "Goodbye!", None, False])

    @unittest.expectedFailure
    def testListFailure2(self):
        self.assertListEqual([2, "Hello!", None], [2, "Hello!"])

    @unittest.expectedFailure
    def testListFailure3(self):
        self.assertListEqual([2, 2.0], "[2, 2.0, 3.0]")

    def testListAlmostEquals(self):
        self.assertListAlmostEqual([1.001, 1.0021], "[1.002, 1.0011]", .001)
        self.assertListAlmostEqual([1.001], "[1.000]", .001)

    @unittest.expectedFailure
    def testListAlmostEqualsFailure(self):
        # this should fail bc that 1.00014 rounds down and 1.0025 rounds up
        self.assertListAlmostEqual([1.0025], [1.0014], .001)

    def testTuple(self):
        self.assertTupleEqual((1, 2), (1, 2))

    @unittest.expectedFailure
    def testTupleFailure(self):
        self.assertTupleEqual((1, 1), (1, 2))

    def testAlmostEquals(self):
        self.assertAlmostEquals(1, 0.8, _delta=.2)

    @unittest.expectedFailure
    def testAlmostEqualsFailure(self):
        self.assertAlmostEquals(1, 1.3, _delta=.2)
