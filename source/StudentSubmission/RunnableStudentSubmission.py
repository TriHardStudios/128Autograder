import code
import os
import sys
from io import StringIO
import tempfile

import psutil


class RunnableStudentSubmission:

    def __init__(self, _stdin: StringIO, _runner: callable, timeout: int = 10):
        self.stdin: StringIO = _stdin
        self.stdout: StringIO = StringIO()
        self.runner: callable = _runner
        self.timeout: int = timeout
        self.timeoutOccurred: bool = False
        self.exception: Exception | None = None

    @staticmethod
    def _runStudentSubmission(_stdinFD: int, _stdoutFD: int, _stderrFD: int | None, _runner: callable):
        # if _runner is not callable:
        #     raise AttributeError("Invalid runner.")

        os.dup2(_stdinFD, sys.stdin.fileno())
        os.dup2(_stdoutFD, sys.stdout.fileno())
        if _stderrFD:
            os.dup2(_stderrFD, sys.stderr.fileno())

        exception: Exception | None = None
        returnVal: object = None
        try:
            returnVal = _runner()
        except Exception as g_ex:
            exception = g_ex

        # todo process and serialize return value

        os.close(_stdinFD)
        os.close(_stdoutFD)
        if _stderrFD:
            os.close(_stderrFD)

        if exception:
            raise exception

        return 0

    def run(self):
        readFD, writeFD = os.pipe()
        stdinFD, stdinPath = tempfile.mkstemp()
        with os.fdopen(stdinFD, 'w') as w:
            for line in self.stdin:
                w.write(line)

        try:
            pid = os.fork()
        except OSError:
            # todo might want to handle a bit differently
            raise

        if pid == 0:
            os.close(readFD)
            try:
                self._runStudentSubmission(stdinFD, writeFD, None, self.runner)
            except Exception as g_ex:
                self.exception = g_ex

            return

        else:
            os.close(writeFD)
            studentSubmissionProcess: psutil.Process = psutil.Process(pid)
            returnValue: int = 0
            try:
                os.waitpid(pid, 0)
                # returnValue = studentSubmissionProcess.wait(self.timeout)

            except psutil.TimeoutExpired:
                self.timeoutOccurred = True
            except Exception as g_ex:
                self.exception = g_ex

            if studentSubmissionProcess.is_running():
                try:
                    studentSubmissionProcess.kill()
                except OSError:
                    # todo prolly should handle this differently
                    raise

            if returnValue != 0:
                if not self.exception:
                    self.exception = \
                        Exception(f"Student submission exited with non-zero exit code. Exit code: {returnValue}")

            childData = os.fdopen(readFD)

            self.stdout.write(childData.read())
            childData.close()

    def getStdOut(self) -> StringIO: return self.stdout

    def getTimeoutOccurred(self) -> bool: return self.timeoutOccurred

    def getExceptions(self) -> Exception: return self.exception
