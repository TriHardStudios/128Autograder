import unittest
from TestingFramework import SingleFunctionMock


class TestSingleFunctionMock(unittest.TestCase):

    def testSideEffect(self):
        def funcToMock():
            return "hello"

        funcToMock = SingleFunctionMock("funcToMock", ["goodbye"])

        self.assertEqual("goodbye", funcToMock())

    def testSideEffectManyCalls(self):
        def funcToMock():
            return "hello"

        sideEffects = [1, 2, 3, 4, 5]

        funcToMock = SingleFunctionMock("funcToMock", sideEffects)

        actual = []
        for _ in range(10):
            actual.append(funcToMock())

        sideEffects.extend([5, 5, 5, 5, 5])

        self.assertEqual(sideEffects, actual)

    def testVoidSideEffectManyCalls(self):
        def funcToMock():
            return "hello"

        funcToMock = SingleFunctionMock("funcToMock", None)

        self.assertIsNone(funcToMock())

    def testCalled(self):
        def funcToMock():
            return "hello"

        funcToMock()

        funcToMock = SingleFunctionMock("funcToMock", None)

        funcToMock()

        funcToMock.assertCalledTimes(1)

    def testCalledWith(self):

        def funcToMock():
            return "hello"

        funcToMock = SingleFunctionMock("funcToMock", None)

        funcToMock(1, 2, 3)

        funcToMock.assertCalledWith(1, 2, 3)

    def testCalledWithManyCalls(self):
        def funcToMock():
            return "hello"

        funcToMock = SingleFunctionMock("funcToMock", None)

        for i in range(10):
            funcToMock(i, i, i)

        funcToMock.assertCalledWith(3, 3, 3)


    def testCalledWithSpy(self):
        def funcToMock(a, b, c):
            return a + b + c

        funcToMockSrc = funcToMock
        funcToMock = SingleFunctionMock("funcToMock", spy=True)

        funcToMock.setSpyFunction(funcToMockSrc)

        result = funcToMock(1, 2, 3)

        self.assertEqual(6, result)
        funcToMock.assertCalledTimes(1)

        

