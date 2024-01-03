import os
from typing import Iterable, List


class MissingOutputDataException(Exception):
    def __init__(self, _outputFileName):
        super().__init__("Output results are NULL.\n"
                         f"Failed to parse results in {_outputFileName}.\n"
                         f"Submission possibly crashed or terminated before harness could write to {_outputFileName}.")

def filterStdOut(stdOut: List[str]) -> List[str]:
    """
    This function takes in a list representing the output from the program. It includes ALL output,
    so lines may appear as 'NUMBER> OUTPUT 3' where we only care about what is right after the OUTPUT statement
    This is adapted from John Henke's implementation

    :param _stdOut: The raw stdout from the program
    :returns: the same output with the garbage removed
    """

    filteredOutput: List[str] = []
    for line in stdOut:
        if "output " in line.lower():
            filteredOutput.append(line[line.lower().find("output ") + 7:])

    return filteredOutput

def detectFileSystemChanges(inFiles: Iterable[str], directoryToCheck: str) -> List[str]:
    files = [os.path.join(directoryToCheck, file) for file in os.listdir(directoryToCheck)]

    outputFiles: List[str] = []

    # This ignores sub folders
    for file in files:
        if os.path.isdir(file):
            continue

        if "__" in file:
            continue

        # ignore hidden files
        if os.path.basename(file)[0] == ".":
            continue

        if file in inFiles:
            continue

        outputFiles.append(file)

    return outputFiles
