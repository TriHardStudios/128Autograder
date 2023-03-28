import math
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
    def _stripOutput(_str: str) -> str:
        if not isinstance(_str, str):
            raise AssertionError(f"Expected a string. Got {type(_str).__qualname__}")

        if "output " in _str.lower():
            _str = _str[7:]

        _str = _str.strip()

        return _str

    @staticmethod
    def _convertStringToList(_str: str) -> list[str]:
        if not isinstance(_str, str):
            raise AssertionError(f"Expected a string. Got {type(_str).__qualname__}")

        _str = Assertions._stripOutput(_str)

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

    @staticmethod
    def _convertIterableFromString(_expected, _actual):
        for i in range(len(_expected)):
            parsedActual = object
            expectedType = type(_expected[i])
            try:
                if isinstance(_actual[i], type(_expected[i])):
                    parsedActual = _actual[i]
                elif _expected[i] is None:
                    if _actual[i] == "None":
                        parsedActual = None
                elif isinstance(_expected[i], bool):
                    parsedActual = True if _actual[i] == "True" else False
                else:
                    parsedActual = expectedType(_actual[i])
            except Exception:
                raise AssertionError(f"Failed to parse {expectedType.__qualname__} from {_actual[i]}")

            _actual[i] = parsedActual

        return _actual

    def _assertIterableEqual(self, _expected, _actual, msg: any = ...):
        for i in range(len(_expected)):
            if _expected[i] != _actual[i]:
                self._raiseFailure("output", _expected[i], _actual[i], msg)

    @staticmethod
    def findPrecision(x: float):
        """
        This function is stolen from stack overflow verbatim - it computes the precision of a float
        """
        max_digits = 14
        int_part = int(abs(x))
        magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
        if magnitude >= max_digits:
            return magnitude
        frac_part = abs(x) - int_part
        multiplier = 10 ** (max_digits - magnitude)
        frac_digits = multiplier + int(multiplier * frac_part + 0.5)
        while frac_digits % 10 == 0:
            frac_digits /= 10
        scale = int(math.log10(frac_digits))
        return magnitude + scale

    def assertMultiLineEqual(self, _expected: str, _actual: str, msg: any = ...) -> None:
        if not isinstance(_expected, str):
            raise AttributeError(f"Expected must be string. Actually is {type(_expected).__qualname__}")
        if not isinstance(_actual, str):
            raise AssertionError(f"Expected a string. Got {type(_actual).__qualname__}")

        if _expected != _actual:
            self._raiseFailure("output", _expected, _actual, msg)

    def _assertListPreCheck(self, _expected: list[any], _actual: list[object] | str, msg: object = ...):
        if not isinstance(_expected, list):
            raise AttributeError(f"Expected must be a list. Actually is {type(_expected).__qualname__}")
        if isinstance(_actual, str):
            _actual = self._convertStringToList(_actual)

        if not isinstance(_actual, list):
            raise AssertionError(f"Expected a list. Got {type(_actual).__qualname__}")

        if len(_expected) != len(_actual):
            self._raiseFailure("number of elements", len(_expected), len(_actual), msg)

        return self._convertIterableFromString(_expected, _actual)

    def assertListEqual(self, _expected: list[any], _actual: list[object] | str, msg: object = ...) -> None:
        _actual = self._assertListPreCheck(_expected, _actual, msg)
        self._assertIterableEqual(_expected, _actual, msg)

    def assertListAlmostEqual(self, _expected: list[any], _actual: list[object] | str, allowedDelta: float, msg: object = ...) -> None:
        _actual = self._assertListPreCheck(_expected, _actual, msg)
        for i in range(len(_expected)):
            if round(abs(_expected[i] - _actual[i]), self.findPrecision(allowedDelta)) > allowedDelta:
                self._raiseFailure(f"output (allowed delta +/- {allowedDelta})", _expected[i], _actual[i], msg)

    def assertTupleEqual(self, _expected: tuple[any, ...], _actual: tuple[object, ...], msg: object = ...) -> None:
        if not isinstance(_expected, tuple):
            raise AttributeError(f"Expected must be a tuple. Actually is {type(_expected).__qualname__}")

        if not isinstance(_actual, tuple):
            raise AssertionError(f"Expected a tuple. Got {type(_actual).__qualname__}")

        if len(_expected) != len(_actual):
            self._raiseFailure("number of elements", len(_expected), len(_actual), msg)

        self._assertIterableEqual(_expected, _actual, msg)

    def assertDictEqual(self, _expected: dict[any, object], _actual: dict[object, object], msg: any = ...) -> None:
        pass

    def assertAlmostEquals(self, _expected: float, _actual: float, _places: int = ..., msg: any = ..., _delta: float = ...) -> None:
        pass

