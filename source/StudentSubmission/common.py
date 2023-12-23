from enum import Enum
from typing import List

class PossibleResults(Enum):
    STDOUT = "stdout"
    RETURN_VAL = "return_val"
    FILE_OUT = "file_out"
    FILE_HASH = "file_hash"
    MOCK_SIDE_EFFECTS = "mock"
    EXCEPTION = "exception"

class ValidationHook(Enum):
    PRE_LOAD = 1
    POST_LOAD = 2
    PRE_BUILD = 3
    POST_BUILD = 4
    VALIDATION = 5


# This is a problem for future me, but basically the pickler is not picking these execeptions correctly. It is passing the message into it, 
# Which also explains that weird error that I was getting eariler in the semester when the MissingFunctionDefination error would appear twice
# we should prolly look into this
class MissingOutputDataException(Exception):
    def __init__(self, _outputFileName):
        super().__init__("Output results are NULL.\n"
                         f"Failed to parse results in {_outputFileName}.\n"
                         f"Submission possibly crashed or terminated before harness could write to {_outputFileName}.")


class MissingFunctionDefinition(Exception):
    def __init__(self, _functionName: str):
        super().__init__(
                f"Failed to find function with name: {_functionName}.\n"
                "Are you missing the function definition?"
        )

class InvalidTestCaseSetupCode(Exception):
    def __init__(self, *args):
        super().__init__(
                "Failed to find 'autograder_setup' function to run.\n"
                "Ensure that your setup code contains a 'autograder_setup' function.\n"
                "This is an autograder error."
        )

class StudentSubmissionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ValidationError(AssertionError):
    @staticmethod
    def combineErrorMessages(exceptions: List[Exception]) -> str:
        msg = ""
        for i, ex in enumerate(exceptions):
            msg += f"{i + 1}. {type(ex).__qualname__}: {ex}\n"

        return msg

    def __init__(self, exceptions: List[Exception]):
        msg = self.combineErrorMessages(exceptions)

        super().__init__("Validation Errors:\n" + msg)

def filterStdOut(_stdOut: list[str]) -> list[str]:
    """
    This function takes in a list representing the output from the program. It includes ALL output,
    so lines may appear as 'NUMBER> OUTPUT 3' where we only care about what is right after the OUTPUT statement
    This is adapted from John Henke's implementation

    :param _stdOut: The raw stdout from the program
    :returns: the same output with the garbage removed
    """

    filteredOutput: list[str] = []
    for line in _stdOut:
        if "output " in line.lower():
            filteredOutput.append(line[line.lower().find("output ") + 7:])

    return filteredOutput
