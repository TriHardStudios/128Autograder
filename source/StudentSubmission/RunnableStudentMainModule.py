import multiprocessing.process
from io import StringIO
from typing import TextIO
import sys


class RunnableStudentMainModule(multiprocessing.Process):

    def __init__(self, _compiledStudentCode, _stdin: StringIO):
        super().__init__(name="Student Submission")
        self.code = _compiledStudentCode
        self.runtimeException: Exception | None = None
        self.capturedStdOutput = StringIO()
        self.capturedStdError = StringIO()
        self.stdin = _stdin

    def run(self):
        self.capturedStdOutput = sys.stdout = StringIO()
        self.capturedStdError = sys.stderr = StringIO()
        sys.stdin = self.stdin
        try:
            exec(self.code, {'__name__': "__main__"}, {'sys': sys})
        except Exception as g_ex:
            self.runtimeException = g_ex

        pass

    def getStdOut(self) -> StringIO: return self.capturedStdOutput
    def getStdErr(self) -> StringIO: return self.capturedStdError

    def stop(self):
        self.terminate()

        if self.is_alive():
            self.kill()
            self.terminate()

    def join(self, timeout: float | None = ...):
        multiprocessing.process.BaseProcess.join(self, timeout)

        if self.runtimeException:
            raise self.runtimeException

