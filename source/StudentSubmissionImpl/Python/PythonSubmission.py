# It finally happened. The great refactoring!

from types import CodeType
from typing import Dict, TypeVar, Set
from StudentSubmission import AbstractStudentSubmission
from .PythonValidators import MainFileValidator
from .common import FileTypeMap

Builder = TypeVar("Builder", bound="StudentSubmission")

class StudentSubmission(AbstractStudentSubmission[CodeType]):
    def __init__(self):
        # might want to make this customizable
        self.ALLOWED_STRICT_MAIN_NAMES = ["main.py", "submission.py"]
        self._allowTestFiles: bool = False
        self._allowRequirements: bool = False
        self._allowLooseMainMatching: bool = False

        self.discoveredFileMap: Dict[FileTypeMap, Set[str]]


        self.addValidator(MainFileValidator(self.ALLOWED_STRICT_MAIN_NAMES))

    def allowTestFiles(self: Builder, allowTestFiles: bool = True) -> Builder:
        self._allowTestFiles = allowTestFiles
        return self

    def allowRequirements(self: Builder, allowRequirements: bool = True) -> Builder:
        self._allowRequirements = allowRequirements
        return self

    def allowLooseMainMatching(self: Builder, allowLooseMainMatching: bool = True) -> Builder:
        self._allowLooseMainMatching = allowLooseMainMatching
        return self


    def doLoad(self):
        return super().doLoad()

    def doBuild(self):
        return super().doBuild()




    def testFilesAllowed(self) -> bool: return self._allowTestFiles
    def requirementsAllowed(self) -> bool: return self._allowRequirements
    def looseMainMatchingAllowed(self) -> bool: return self._allowLooseMainMatching
    def getDiscoveredFileMap(self) -> Dict[FileTypeMap, Set[str]]: return self.discoveredFileMap
