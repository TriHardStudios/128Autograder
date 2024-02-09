from pathlib import Path
from typing import List
import subprocess
from StudentSubmission.ISubmissionProcess import ISubmissionProcess
from StudentSubmissionImpl.C.CRunners import MainRunner
from Executors.Environment import ExecutionEnvironment

class CSubmissionProcess(ISubmissionProcess):
    def setup(self, environment: ExecutionEnvironment, runner: MainRunner): # pyright: ignore[reportIncompatibleMethodOverride]
        self.absWorkingDirectory: str = str(Path(environment.SANDBOX_LOCATION).resolve())
        self.stdOut: str = ""
        self.stdIn: List[str] = environment.stdin
        self.runner = runner
        # currently only stdOut is only supported
        
    def run(self):
        try:
            subprocess.run(self.runner.getSubmission(), cwd=self.absWorkingDirectory, check=True, )
        except:
            pass

    def populateResults(self, environment: ExecutionEnvironment):
        return super().populateResults(environment)

    def cleanup(self):
        return super().cleanup()

    @classmethod
    def processAndRaiseExceptions(cls, environment: ExecutionEnvironment):
        return super().processAndRaiseExceptions(environment)
