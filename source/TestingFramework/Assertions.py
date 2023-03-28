import re
import unittest


class Assertions(unittest.TestCase):

    def __init__(self, _testResults):
        super().__init__(_testResults)
        self.addTypeEqualityFunc(str, self.assertMultiLineEqual)
        self.addTypeEqualityFunc(dict, self.assertDictEqual)
        self.addTypeEqualityFunc(list, self.assertListEqual)
        self.addTypeEqualityFunc(tuple, self.assertTupleEqual)

    @staticmethod
    def _convertStringToList(_str: str) -> list[str]:
        if not isinstance(_str, str):
            raise AssertionError(f"Expected a string. Got {type(_str).__qualname__}")

        if "output " in _str.lower():
            _str = _str[7:]

        if "[" in _str:
            _str = _str[1:]
        if "]" in _str:
            _str = _str[:-1]
        _str = _str.strip()

        parsedList: list[str] = _str.split(",")
        charsToRemove = re.compile("[\"']")
        parsedList = [el.strip() for el in parsedList]
        parsedList = [re.sub(charsToRemove, "", el) for el in parsedList]
        return parsedList

    @staticmethod
    def _raiseFailure(_shortDescription, _expectedObject, _actualObject, msg):
        errorMsg = f"Incorrect {_shortDescription}.\n" + \
                   f"Expected {_shortDescription}: {_expectedObject}\n" + \
                   f"Your {_shortDescription}    : {_actualObject}"
        if msg:
            errorMsg += "\n\n" + str(msg)

        raise AssertionError(errorMsg)

    def assertMultiLineEqual(self, _expected: str, _actual: str, msg: any = ...) -> None:
        if not isinstance(_expected, str):
            raise AttributeError(f"Expected must be string. Actually is {type(_expected).__qualname__}")
        if not isinstance(_actual, str):
            raise AssertionError(f"Expected a string. Got {type(_actual).__qualname__}")

        if _expected != _actual:
            self._raiseFailure("output", _expected, _actual, msg)

    def assertListEqual(self, _expected: list[any], _actual: list[object] | str, msg: object = ...) -> None:
        if not isinstance(_expected, list):
            raise AttributeError(f"Expected must be a list. Actually is {type(_expected).__qualname__}")
        if isinstance(_actual, str):
            _actual = self._convertStringToList(_actual)

        if not isinstance(_actual, list):
            raise AssertionError(f"Expected a list. Got {type(_actual).__qualname__}")

        if len(_expected) != len(_actual):
            self._raiseFailure("number of elements", len(_expected), len(_actual), msg)

        for i in range(len(_expected)):
            expectedType = type(_expected[i])
            try:
                if _expected[i] is None:
                    if _actual[i] == "None":
                        _actual[i] = None
                else:
                    parsedActual = expectedType(_actual[i])
            except Exception:
                raise AssertionError(f"Failed to parse {expectedType.__qualname__} from {_actual[i]}")

            if _expected[i] != parsedActual:
                self._raiseFailure("list element", _expected[i], parsedActual, msg)


    def assertTupleEqual(self, _expected: tuple[any, ...], _actual: tuple[object, ...], msg: object = ...) -> None:
        pass

    def assertDictEqual(self, _expected: dict[any, object], _actual: dict[object, object], msg: any = ...) -> None:
        pass
