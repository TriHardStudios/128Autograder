import multiprocessing
import os
import sys
from io import StringIO


class StudentSubmissionProcess(multiprocessing.Process):
    def __init__(self, _runner, _inputFD, _outputFD, timeout: int = 10):
        super().__init__(name="Student Submission")
        self.runner = _runner
        self.inputFD = _inputFD
        self.outputFD = _outputFD
        self.exception: Exception | None = None
        self.timeout = timeout

    def _serialize(self, _object: object) -> str:
        pass

    def run(self):
        try:
            os.dup2(self.inputFD, sys.stdin.fileno())
            os.dup2(self.outputFD, sys.stdout.fileno())
        except OSError:
            raise

        returnValue: object = None
        try:
            returnValue = self.runner()
        except EOFError:
            pass  # todo - need to handle eof- raising it doesnt work :(
        except Exception as g_ex:
            self.exception = g_ex

        if returnValue:
            print(self._serialize(returnValue))  # I dont like this approach
        # not sure if we need to close the pipe

        os.close(self.inputFD)
        os.close(self.outputFD)

        if self.exception:
            raise self.exception

    def join(self, **kwargs):
        multiprocessing.Process.join(self, timeout=self.timeout)

    def terminate(self):
        # SigKill - cant be caught
        multiprocessing.Process.kill(self)
        # Checks to see if we are killed and cleans up process
        multiprocessing.Process.terminate(self)
        # Clean up the zombie
        multiprocessing.Process.join(self, timeout=0)


class RunnableStudentSubmission:

    def __init__(self, _stdin: StringIO, _runner: callable, timeout: int = 10):
        self.stdin: StringIO = _stdin
        self.stdout: StringIO = StringIO()
        self.stdinR, self.stdinW = os.pipe()
        self.stdoutR, self.stdoutW = os.pipe()
        self.studentSubmissionProcess = StudentSubmissionProcess(_runner, self.stdinR, self.stdoutW, timeout)
        self.timeoutOccurred: bool = False
        self.exception: Exception | None = None

    def run(self):
        readFromStdoutPipe = os.fdopen(self.stdoutR, 'r')
        writeToStdinPipe = os.fdopen(self.stdinW, 'w')

        try:
            for line in self.stdin:
                writeToStdinPipe.write(line)

            writeToStdinPipe.close()

            self.studentSubmissionProcess.start()

            # close the ends that we don't need
            os.close(self.stdinR)
            os.close(self.stdoutW)

            self.studentSubmissionProcess.join()

            if self.studentSubmissionProcess.is_alive():
                self.studentSubmissionProcess.terminate()
                self.timeoutOccurred = True

            # While not completely required, reading the output when
            #  we are timed out and will fail anyway
            if not self.timeoutOccurred:
                for line in readFromStdoutPipe:
                    self.stdout.write(line)

            readFromStdoutPipe.close()

        except OSError:
            raise
        except Exception as g_ex:
            self.exception = g_ex

    def getStdOut(self) -> StringIO:
        return self.stdout

    def getTimeoutOccurred(self) -> bool:
        return self.timeoutOccurred

    def getExceptions(self) -> Exception:
        return self.exception
