from enum import Enum
from typing import Iterable

class FileTypeMap(Enum):
    TEST_FILES = 1
    PYTHON_FILES = 2
    REQUIREMENTS = 3
    
class NoPyFilesError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Expected at least one `.py` file. Received 0.\n"
            "Are you writing your code in a file that ends with `.py`?"
        )

class MissingMainFileError(Exception):
    def __init__(self, expectedMains: Iterable[str], files: Iterable[str]) -> None:
        super().__init__(
            f"Expected file named {'or'.join(file for file in expectedMains)}. Received: {','.join(file for file in files)}"
        )

class TooManyFilesError(Exception):
    def __init__(self, files: Iterable[str]) -> None:
        super().__init__(
            f"Expected one `.py` file. Received: {','.join(file for file in files)}"
        )

