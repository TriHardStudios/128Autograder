from typing import List
from StudentSubmission.AbstractValidator import AbstractValidator, ValidationHook
from StudentSubmissionImpl.C.common import FileTypeMap, MissingMakefile, TooManyMakefiles

class MakefileExists(AbstractValidator):
    @staticmethod
    def getValidationHook() -> ValidationHook:
        return ValidationHook.POST_LOAD


    def __init__(self):
        super().__init__()
        self.makefiles: List[str] = []

    def setup(self, studentSubmission):
        self.makefiles = studentSubmission.getFileMap()[FileTypeMap]

    def run(self):
        if len(self.makefiles) == 0:
            self.addError(MissingMakefile())

        if len(self.makefiles) > 1:
            self.addError(TooManyMakefiles())



        
