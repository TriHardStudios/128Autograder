import os
from re import Pattern
import re
from typing import Dict, List, TypeVar, Iterable

from StudentSubmission.AbstractStudentSubmission import AbstractStudentSubmission
from StudentSubmissionImpl.C.common import FileTypeMap

Builder = TypeVar("Builder", bound="CSubmission")

def filterSearchResults(*args) -> bool:
    return True

class CSubmission(AbstractStudentSubmission[str]):
    MAKEFILE_REGEX: Pattern = re.compile(r"^[Mm]akefile$")
    CPP_SUBMISSION_REGEX: Pattern = re.compile(r"^[\w\d]+\.cpp$")
    HPP_SUBMISSION_REGEX: Pattern = re.compile(r"^[\w\d]+\.hpp$")
    C_SUBMISSION_REGEX: Pattern = re.compile(r"^[\w\d]+\.c$")
    H_SUBMISSION_REGEX: Pattern = re.compile(r"^[\w\d]+\.h$")

    def __init__(self):
        super().__init__()

        self.makefilesEnabled: bool = False
        self.cMatchingEnabled: bool = False
        self.cppMatchingEnabled: bool = False

        self.discoveredFileMap: Dict[FileTypeMap, List[str]]



    def enableMakefile(self: Builder, enableMakefile: bool = True) -> Builder:
        self.makefilesEnabled = enableMakefile

        return self

    def enableCMatching(self: Builder, enableCMatching: bool = True) -> Builder:
        self.cMatchingEnabled = enableCMatching
        
        return self

    def enableCppMatching(self: Builder, enableCppMatching: bool = True) -> Builder:
        self.cppMatchingEnabled = enableCppMatching

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
            if os.path.isdir(os.path.join(directoryToSearch, path)):
                self._discoverSubmittedFiles(os.path.join(directoryToSearch, path))
                continue

            if self.getMakeFileEnabled() and self.MAKEFILE_REGEX.match(path):
                self._addFileToMap(os.path.join(directoryToSearch, path), FileTypeMap.MAKEFILE)
                continue

            if self.getCMatchingEnabled() and self.C_SUBMISSION_REGEX.match(path):
                self._addFileToMap(os.path.join(directoryToSearch, path), FileTypeMap.C_FILE)
                continue

            if self.getCppMatchingEnabled() and self.CPP_SUBMISSION_REGEX.match(path):
                self._addFileToMap(os.path.join(directoryToSearch, path), FileTypeMap.CPP_FILE)
                continue

            if self.getCppMatchingEnabled() and self.HPP_SUBMISSION_REGEX.match(path):
                self._addFileToMap(os.path.join(directoryToSearch, path), FileTypeMap.HPP_FILE)
                continue

            if (self.getCppMatchingEnabled() or self.getCMatchingEnabled()) and self.H_SUBMISSION_REGEX.match(path):
                self._addFileToMap(os.path.join(directoryToSearch, path), FileTypeMap.H_FILE)
                continue

    def doLoad(self):
        pass

    def doBuild(self):
        pass

    def getSubmissionRoot(self) -> str:
        return super().getSubmissionRoot()

    def getMakeFileEnabled(self) -> bool: return self.makefilesEnabled
    def getCMatchingEnabled(self) -> bool: return self.cMatchingEnabled
    def getCppMatchingEnabled(self) -> bool: return self.cppMatchingEnabled
    def getExecutableSubmission(self) -> str:
        return ""

