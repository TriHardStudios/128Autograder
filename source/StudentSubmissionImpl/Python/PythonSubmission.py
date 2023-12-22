# It finally happened. The great refactoring!

import os
import re
from types import CodeType
from typing import Dict, Iterable, List, Optional, TypeVar
from StudentSubmission import AbstractStudentSubmission
from .PythonValidators import PythonFileValidator, PackageValidator, RequirementsValidator
from .common import FileTypeMap

Builder = TypeVar("Builder", bound="StudentSubmission")

def filterSearchResults(path: str) -> bool:
    # ignore hidden files
    if path[0] == '.':
        return False

    # ignore python cache files
    if "__" in path:
        return False

    if " " in path:
        return False

    return True


class StudentSubmission(AbstractStudentSubmission[CodeType]):
    ALLOWED_STRICT_MAIN_NAMES = ["main.py", "submission.py"]

    # we are not allowing any files with a space in them
    PYTHON_FILE_REGEX: re.Pattern = re.compile(r"^(\w|-)+\.py$")
    # the requirements.txt file MUST be in the root of the student's submission
    REQUIREMENTS_REGEX: re.Pattern = re.compile(r"^requirements\.txt$")
    # test files follow similar rules to python files, but must start with 'test'
    TEST_FILE_REGEX: re.Pattern = re.compile(r"^test(\w|-)*\.py$")
    # this allows versioned and non versioned packages, but disallows local packages
    REQUIREMENTS_LINE_REGEX: re.Pattern = re.compile(r"^(\w|-)+(==)?(\d+\.?){0,3}$")

    def __init__(self):
        super().__init__()

        self._allowTestFiles: bool = False
        self._allowRequirements: bool = False
        self._allowLooseMainMatching: bool = False

        self.discoveredFileMap: Dict[FileTypeMap, List[str]] = {}

        self.extraPackages: Dict[str, str] = {}

        self.addValidator(PythonFileValidator(self.ALLOWED_STRICT_MAIN_NAMES))
        self.addValidator(RequirementsValidator())
        self.addValidator(PackageValidator())

    def allowTestFiles(self: Builder, allowTestFiles: bool = True) -> Builder:
        self._allowTestFiles = allowTestFiles
        return self

    def allowRequirements(self: Builder, allowRequirements: bool = True) -> Builder:
        self._allowRequirements = allowRequirements
        return self

    def allowLooseMainMatching(self: Builder, allowLooseMainMatching: bool = True) -> Builder:
        self._allowLooseMainMatching = allowLooseMainMatching
        return self

    def addPackage(self: Builder, packageName: str, packageVersion: Optional[str] = None) -> Builder:
        self.extraPackages[packageName] = packageVersion if packageVersion is not None else ""
        return self

    def addPackages(self: Builder, packageMap: Dict[str, str]) -> Builder:
        self.extraPackages.update(packageMap)
        return self

    def _addFileToMap(self, path: str, fileType: FileTypeMap) -> None:
        if fileType not in self.discoveredFileMap.keys():
            self.discoveredFileMap[fileType] = []

        self.discoveredFileMap[fileType].append(path)

    def _discoverSubmittedFiles(self, directoryToSearch: str) -> None:
        pathesToVisit: Iterable[str] = filter(filterSearchResults, os.listdir(directoryToSearch))

        if not pathesToVisit:
            return

        for path in pathesToVisit:
            if os.path.isdir(path):
                self._discoverSubmittedFiles(os.path.join(directoryToSearch, path))
                continue

            if self.testFilesAllowed() and self.TEST_FILE_REGEX.match(path):
                self._addFileToMap(os.path.join(directoryToSearch, path), FileTypeMap.TEST_FILES)
                continue
            
            if self.PYTHON_FILE_REGEX.match(path):
                self._addFileToMap(os.path.join(directoryToSearch, path), FileTypeMap.PYTHON_FILES)
                continue

            if self.requirementsAllowed() and self.REQUIREMENTS_REGEX.match(path):
                self._addFileToMap(os.path.join(directoryToSearch, path), FileTypeMap.REQUIREMENTS)

    def _loadRequirements(self) -> None:
        if not self.requirementsAllowed() or FileTypeMap.REQUIREMENTS not in self.discoveredFileMap:
            return

        with open(self.discoveredFileMap[FileTypeMap.REQUIREMENTS][0], 'r') as r:
            # we are going to ignore any paths that aren't set up as package==version
            for line in r:
                # we might want to add logging + telementry
                if not self.REQUIREMENTS_LINE_REGEX.match(line):
                    # we might want to add some logging here
                    continue
                line = line.split('==')

                self.addPackage(line[0], line[1] if len(line) == 2 else None)

    def doLoad(self):
        self._discoverSubmittedFiles(self.getSubmissionRoot())
        self._loadRequirements()


    def doBuild(self):
        pass

    def getExecutableSubmission(self) -> CodeType:
        return compile("", "submission", "exec")





    def testFilesAllowed(self) -> bool: return self._allowTestFiles
    def requirementsAllowed(self) -> bool: return self._allowRequirements
    def looseMainMatchingAllowed(self) -> bool: return self._allowLooseMainMatching
    def getDiscoveredFileMap(self) -> Dict[FileTypeMap, List[str]]: return self.discoveredFileMap
    def getExtraPackages(self) -> Dict[str, str]: return self.extraPackages
