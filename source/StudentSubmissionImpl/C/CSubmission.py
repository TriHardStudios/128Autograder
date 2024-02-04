import os
from re import Pattern
import re
from typing import Dict, List, TypeVar, Iterable

from StudentSubmission.AbstractStudentSubmission import AbstractStudentSubmission
from StudentSubmissionImpl.C.common import FileTypeMap

Builder = TypeVar("Builder", bound="CSubmission")

class CSubmission(AbstractStudentSubmission[str]):
    MAKEFILE_REGEX: Pattern = re.compile(r"^[Mm]akefile$")

    def __init__(self):
        super().__init__()

        self.makefilesEnabled: bool = False

        self.discoveredFileMap: Dict[FileTypeMap, List[str]]

    def enableMakefile(self: Builder, enableMakefile: bool = True) -> Builder:
        self.makefilesEnabled = enableMakefile

        return self

    def _addFileToMap(self, path: str, fileType: FileTypeMap) -> None:
        if fileType not in self.discoveredFileMap.keys():
            self.discoveredFileMap[fileType] = []

        self.discoveredFileMap[fileType].append(path)

    def _discoverSubmittedFiles(self, directoryToSearch: str) -> None:
        discoveredFiles = os.listdir(directoryToSearch)
        # makefiles must be located in submission root
        
        for file in discoveredFiles:
            if os.path.isdir(os.path.join(directoryToSearch, file)):
                continue

            if os.path.isfile(os.path.join(directoryToSearch, file)) and self.MAKEFILE_REGEX.match(file):
                self._addFileToMap(os.path.join(directoryToSearch, file), FileTypeMap.MAKEFILE)

    def doLoad(self):
        self._discoverSubmittedFiles(self.submissionRoot)

    def doBuild(self):
        current_directory = os.getcwd()
        pass

    def getSubmissionRoot(self) -> str:
        return super().getSubmissionRoot()

    def getMakeFileEnabled(self) -> bool: return self.makefilesEnabled
    def getExecutableSubmission(self) -> str:
        return ""

    def getFileMap(self) -> Dict[FileTypeMap, List[str]]: return self.discoveredFileMap

