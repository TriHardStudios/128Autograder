import os
from StudentSubmission.Runners import IRunner

class MainRunner(IRunner[str]):
    def __init__(self):
        self.submissionPath: str = ""

    def setSubmission(self, submission: str):
        self.submissionPath = submission

    def getSubmission(self): return self.submissionPath


        


