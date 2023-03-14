import unittest


class Assertions(unittest.TestCase):

    def __init__(self, _testResults):
        super().__init__(_testResults)
        self.addTypeEqualityFunc(str, self.assertMultiLineEqual)
        self.addTypeEqualityFunc(dict, self.assertDictEqual)
        self.addTypeEqualityFunc(list, self.assertListEqual)
        self.addTypeEqualityFunc(tuple, self.assertTupleEqual)

    def assertMultiLineEqual(self, _expected: str, _actual: str, msg: object = ...) -> None:
        if not isinstance(_expected, str):
            raise AttributeError(f"Expected must be string. Actually is {type(_expected)}")
        if not isinstance(_actual, str):
            raise AssertionError(f"Expected a string. Got {type(_actual)}")

        if _expected != _actual:
            errorMsg = f"Incorrect Output.\n" + \
                       f"Expected Output: {_expected}" + \
                       f"Your Output    : {_actual}"
            if msg:
                errorMsg += "\n\n" + str(msg)

            raise AssertionError(errorMsg)

    def assertListEqual(self, _expected: list[object], _actual: list[object], msg: object = ...) -> None:
        pass

    def assertTupleEqual(self, _expected: tuple[object, ...], _actual: tuple[object, ...], msg: object = ...) -> None:
        pass

    def assertDictEqual(self, _expected: dict[object, object], _actual: dict[object, object],
                        msg: object = ...) -> None:
        pass
