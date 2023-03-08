import multiprocessing
import multiprocessing.shared_memory
import os
import sys
import traceback
import dill
from io import StringIO


class StudentSubmissionProcess(multiprocessing.Process):
    def __init__(self, _runner, _stdinSharedMemName, _stdoutSharedMemName, _otherDataMemName, timeout: int = 10):
        super().__init__(name="Student Submission")
        self.runner = _runner
        self.stdinSharedMemName = _stdinSharedMemName
        self.stdoutSharedMemName = _stdoutSharedMemName
        self.otherDataMemName = _otherDataMemName
        self.timeout = timeout

    def _serialize(self, _object: object) -> str:
        pass

    def run(self):
        sharedStdin = multiprocessing.shared_memory.ShareableList(name=self.stdinSharedMemName)
        sys.stdin = StringIO("".join([line + "\n" for line in sharedStdin]))
        sharedStdin.shm.close()
        sharedStdin.shm.unlink()

        stdout = sys.stdout = StringIO()

        returnValue: object = None
        exception: Exception | None = None
        try:
            returnValue = self.runner()
        except EOFError:
            pass  # todo - need to handle eof- raising it doesnt work :(
        except RuntimeError as rt_er:
            exception = rt_er
        except Exception as g_ex:
            exception = g_ex

        otherData: list[str] = [dill.dumps(exception), dill.dumps(returnValue)]

        sharedOtherData = multiprocessing.shared_memory.ShareableList(otherData, name=self.otherDataMemName)
        sharedOtherData.shm.close()

        capturedStdout = []
        stdout.seek(0)
        for line in stdout:
            capturedStdout.append(line)

        sharedStdout = multiprocessing.shared_memory.ShareableList(capturedStdout, name=self.stdoutSharedMemName)
        sharedStdout.shm.close()

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

    def __init__(self, _stdin: list[str], _runner: callable, timeout: int = 10):
        self.stdin: list[str] = _stdin
        self.stdout: StringIO = StringIO()
        self.stdoutSharedName = "sub_stdout"
        self.stdinSharedName = "sub_stdin"
        self.otherDataMemName = "sub_other"
        self.studentSubmissionProcess = StudentSubmissionProcess(
            _runner,
            self.stdinSharedName, self.stdoutSharedName, self.otherDataMemName,
            timeout)

        self.timeoutOccurred: bool = False
        self.exception: Exception | None = None
        self.returnData: object | None = None

    def run(self):

        sharedStdin = multiprocessing.shared_memory.ShareableList(self.stdin, name=self.stdinSharedName)
        sharedStdin.shm.close()

        self.studentSubmissionProcess.start()

        self.studentSubmissionProcess.join()

        if self.studentSubmissionProcess.is_alive():
            self.studentSubmissionProcess.terminate()
            self.timeoutOccurred = True

        if not self.timeoutOccurred:
            capturedStdoutFromChild = multiprocessing.shared_memory.ShareableList(name=self.stdoutSharedName)
            for el in capturedStdoutFromChild:
                self.stdout.write(el)

            capturedStdoutFromChild.shm.close()
            capturedStdoutFromChild.shm.unlink()

            capturedOtherData = multiprocessing.shared_memory.ShareableList(name=self.otherDataMemName)
            self.exception = dill.loads(capturedOtherData[0])
            self.returnData = dill.loads(capturedOtherData[1])
            capturedOtherData.shm.close()
            capturedOtherData.shm.unlink()

    def getStdOut(self) -> StringIO:
        return self.stdout

    def getTimeoutOccurred(self) -> bool:
        return self.timeoutOccurred

    def getExceptions(self) -> Exception:
        return self.exception

    def getReturnData(self) -> object:
        return self.returnData
