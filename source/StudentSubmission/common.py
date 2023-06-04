from enum import Enum


class PossibleResults(Enum):
    STDOUT = "stdout"
    RETURN_VAL = "return_val"
    FILE_OUT = "file_out"
    MOCK_SIDE_EFFECTS = "mock"
    EXCEPTION = "exception"


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
