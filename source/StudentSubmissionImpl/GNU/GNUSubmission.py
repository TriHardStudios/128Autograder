from re import Pattern
import re

from StudentSubmission.AbstractStudentSubmission import AbstractStudentSubmission

class GNUSubmission(AbstractStudentSubmission[Any]):
    MAKEFILE_REGEX: Pattern = re.compile(r"^Makefile$")
    BUILD_REGEX: Pattern = re.compile(r"^Build\.sh$")

    def __init__(self):
        super().__init__()

    def doLoad(self):
        pass

    def doBuild(self):
        pass

    def getSubmissionRoot(self) -> str:
        return super().getSubmissionRoot()

