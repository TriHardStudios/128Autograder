from typing import Dict, Set, List
from StudentSubmission import AbstractValidator
from StudentSubmission.common import ValidationHook
from .common import FileTypeMap, MissingMainFileError, NoPyFilesError, TooManyFilesError
from .PythonSubmission import StudentSubmission

class MainFileValidator(AbstractValidator):

    @staticmethod
    def getValidationHook() -> ValidationHook:
        return ValidationHook.POST_LOAD

    def __init__(self, allowedMainNames: List[str]):
        super().__init__()
        self.ALLOWED_MAIN_NAMES = allowedMainNames
        self.pythonFiles: Dict[FileTypeMap, Set[str]] = {}
        self.looseMainMatchingAllowed: bool = False

    def setup(self, studentSubmission: StudentSubmission):
        submissionFiles = studentSubmission.getDiscoveredFileMap()
        self.looseMainMatchingAllowed = studentSubmission.looseMainMatchingAllowed()

        if studentSubmission.testFilesAllowed():
            self.pythonFiles[FileTypeMap.TEST_FILES] = submissionFiles[FileTypeMap.TEST_FILES]

        if FileTypeMap.PYTHON_FILES not in submissionFiles:
            submissionFiles[FileTypeMap.PYTHON_FILES] = set() 

        self.pythonFiles[FileTypeMap.PYTHON_FILES] = submissionFiles[FileTypeMap.PYTHON_FILES]

    def run(self):
        if not self.pythonFiles[FileTypeMap.PYTHON_FILES]:
            self.addError(NoPyFilesError())
            return

        if self.looseMainMatchingAllowed and len(self.pythonFiles[FileTypeMap.PYTHON_FILES]) > 1:
            self.addError(TooManyFilesError(self.pythonFiles[FileTypeMap.PYTHON_FILES]))
            return

        if not any(file in self.pythonFiles[FileTypeMap.PYTHON_FILES] for file in self.ALLOWED_MAIN_NAMES):
            self.addError(MissingMainFileError(self.ALLOWED_MAIN_NAMES, self.pythonFiles[FileTypeMap.PYTHON_FILES]))
            return


class RequirementsValidator(AbstractValidator):
    @staticmethod
    def getValidationHook() -> ValidationHook:
        return ValidationHook.POST_BUILD


