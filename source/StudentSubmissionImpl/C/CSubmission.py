import os
from re import Pattern
import re
from typing import Dict, List, TypeVar
import subprocess

from StudentSubmission.AbstractStudentSubmission import AbstractStudentSubmission
from StudentSubmissionImpl.C.common import FileTypeMap, decodeBytes
from StudentSubmissionImpl.C.CValidators import ExecutableCreated, MakeAvailable, MakefileExists

Builder = TypeVar("Builder", bound="CSubmission")

class CSubmission(AbstractStudentSubmission[str]):
    MAKEFILE_REGEX: Pattern = re.compile(r"^[Mm]akefile$")

    def __init__(self, submissionName: str):
        super().__init__()

        self.makefilesEnabled: bool = False
        self.buildTimeout: int = 10
        self.submissionName: str = submissionName
        self.cleanTargetName: str = "clean"

        self.discoveredFileMap: Dict[FileTypeMap, List[str]] = {
            FileTypeMap.MAKEFILE: [],
            FileTypeMap.EXECUTABLE: [],
        }

        self.addValidator(MakeAvailable())
        self.addValidator(MakefileExists())
        self.addValidator(ExecutableCreated())

    def enableMakefile(self: Builder, enableMakefile: bool = True) -> Builder:
        self.makefilesEnabled = enableMakefile
        return self

    def setBuildTimeout(self: Builder, buildTimeout: int) -> Builder:
        self.buildTimeout = buildTimeout
        return self
    
    def setCleanTargetName(self: Builder, cleanTarget: str) -> Builder:
        self.cleanTargetName = cleanTarget
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

    def _discoverBuiltFiles(self, directoryToSearch: str) -> None:
        # allow windows format as well
        discoveredFiles = os.listdir(directoryToSearch)

        for file in discoveredFiles:
            path = os.path.join(directoryToSearch, file)
            # allow searching in ./bin
            if file[-3:] == "bin" and os.path.isdir(path):
                self._discoverBuiltFiles(path)
                continue
            if os.path.isdir(path):
                continue

            if os.path.isfile(path) and file[0:len(self.submissionName)] == self.submissionName:
                self._addFileToMap(path, FileTypeMap.EXECUTABLE)

    def doLoad(self):
        self._discoverSubmittedFiles(self.submissionRoot)

    def doBuild(self):
        current_directory = os.getcwd()
        os.chdir(self.submissionRoot)

        # we dont care if the clean target passes or fails
        subprocess.run([f"make", self.cleanTargetName], timeout=self.buildTimeout, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        try:
            # we only care if the main building succeeds
            subprocess.run(["make"], check=True, timeout=self.buildTimeout, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            os.chdir(current_directory)
            raise Exception(f"Failed to build!\n{decodeBytes(e.output)}\n{decodeBytes(e.stderr)}")

        os.chdir(current_directory)

        self._discoverBuiltFiles(self.submissionRoot)

    def getSubmissionRoot(self) -> str:
        return super().getSubmissionRoot()

    def getMakeFileEnabled(self) -> bool: return self.makefilesEnabled
    def getSubmissionName(self) -> str: return self.submissionName
    def getExecutableSubmission(self) -> str:
        return self.discoveredFileMap[FileTypeMap.EXECUTABLE][0]

    def getFileMap(self) -> Dict[FileTypeMap, List[str]]: return self.discoveredFileMap

