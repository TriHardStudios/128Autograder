from enum import Enum


class PossibleResults(Enum):
    STDOUT = "stdout"
    RETURN_VAL = "return_val"
    FILE_OUT = "file_out"
    MOCK_SIDE_EFFECTS = "mock"
    EXCEPTION = "exception"


class MissingOutputDataException(Exception):
    def __init__(self, _outputFileName):
        super().__init__("Output results are NULL.\n"
                         f"Failed to parse results in {_outputFileName}.\n"
                         f"Submission possibly crashed or terminated before harness could write to {_outputFileName}.")


class MissingFunctionDefinition(Exception):
    def __init__(self, _functionName: str):
        self.functionName = _functionName

    def __str__(self):
        return (f"Failed to find function with name: {self.functionName}.\n"
                "Are you missing the function definition?")


class InvalidTestCaseSetupCode(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return ("Failed to find 'autograder_setup' function to run.\n"
                "Ensure that your setup code contains a 'autograder_setup' function.\n"
                "This is an autograder error.")


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
