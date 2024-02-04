from enum import Enum


class FileTypeMap(Enum):
    MAKEFILE = 0


class MissingMakefile(Exception):
    def __init__(self) -> None:
        super().__init__("No makefiles found!\nEnsure that there is exactly 1 makefiles in the submission root.")

class TooManyMakefiles(Exception):
    def __init__(self) -> None:
        super().__init__("Too many makefiles found!\nEnsure that there is exactly 1 makefile in the submission root.")
