from typing import List, Optional
import subprocess
from StudentSubmission.AbstractValidator import AbstractValidator, ValidationHook
from StudentSubmissionImpl.C.common import FileTypeMap, MissingExecutable, TooManyExecutables, decodeBytes, MissingMakefile, TooManyMakefiles, MakeUnavailable

class MakeAvailable(AbstractValidator):
    @staticmethod
    def getValidationHook() -> ValidationHook:
        return ValidationHook.PRE_LOAD

    def __init__(self):
        super().__init__()
        self.usingMake: bool = False

    def setup(self, studentSubmission):
        self.usingMake = studentSubmission.getMakeFileEnabled()

    def run(self):
        if not self.usingMake:
            return

        command = ["make --version"]

        try:
            subprocess.run(command, check=True, shell=True, timeout=1,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            self.addError(MakeUnavailable(decodeBytes(e.output) + "\n" + decodeBytes(e.stderr)))

class MakefileExists(AbstractValidator):
    @staticmethod
    def getValidationHook() -> ValidationHook:
        return ValidationHook.POST_LOAD


    def __init__(self):
        super().__init__()
        self.makefiles: List[str] = []

    def setup(self, studentSubmission):
        self.makefiles = studentSubmission.getFileMap()[FileTypeMap.MAKEFILE]

    def run(self):
        if len(self.makefiles) == 0:
            self.addError(MissingMakefile())

        if len(self.makefiles) > 1:
            self.addError(TooManyMakefiles())

class ExecutableCreated(AbstractValidator):
    @staticmethod
    def getValidationHook() -> ValidationHook:
        return ValidationHook.POST_BUILD

    def __init__(self):
        super().__init__()
        self.executableFiles: List[str] = []
        self.executableName: str = ""

    def setup(self, studentSubmission):
        self.executableFiles = studentSubmission.getFileMap()[FileTypeMap.EXECUTABLE]
        self.executableName = studentSubmission.getSubmissionName()

    def run(self):
        if len(self.executableFiles) == 0:
            self.addError(MissingExecutable(self.executableName))

        if len(self.executableFiles) > 1:
            self.addError(TooManyExecutables(self.executableFiles))
