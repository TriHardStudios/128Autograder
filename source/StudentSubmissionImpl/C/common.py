from enum import Enum
from typing import Optional


class FileTypeMap(Enum):
    MAKEFILE = 0
    EXECUTABLE = 1


def decodeBytes(rawOutput: Optional[bytes]) -> str:
    if rawOutput is None:
        rawOutput = b""

    strOutput = rawOutput.decode("utf-8")
    return strOutput

class MakeUnavailable(Exception):
    def __init__(self, makeOutput) -> None:
        super().__init__(f"Unable to call Make!\nUnable to build. Please ensure that all required packages are installed.\n{makeOutput}")

class MissingMakefile(Exception):
    def __init__(self) -> None:
        super().__init__("No makefiles found!\nEnsure that there is exactly 1 makefiles in the submission root.")

class TooManyMakefiles(Exception):
    def __init__(self) -> None:
        super().__init__("Too many makefiles found!\nEnsure that there is exactly 1 makefile in the submission root.")

class MissingExecutable(Exception):
    def __init__(self, expectedName) -> None:
        super().__init__(f"No executable found with name: `{expectedName}`\nEnsure that your makefile is setup to generate an executable with name `{expectedName}`.")

class TooManyExecutables(Exception):
    def __init__(self, files) -> None:
        super().__init__(f"Too many executable files found! Found: {', '.join(file for file in files)}.")
