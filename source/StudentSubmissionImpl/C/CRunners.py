import os
from typing import Tuple, Optional, Any
from StudentSubmission.Runners import IRunner

class MainRunner(IRunner[str]):
    def __init__(self):
        self.submissionPath: str = ""
        self.parameters: Optional[Tuple[Any]] = None

    def setSubmission(self, submission: str):
        self.submissionPath = submission

    def setParameters(self, parameters: Tuple[Any]):
        self.parameters = parameters

    def getSubmission(self): return self.submissionPath


        


