"""
This module provides an interface for running student submissions as processes.

This module utilizes shared memory to share data from the parent and the child. The way it is currently implemented
guarantees that no conflicts will occur with the pattern. This is because the parent waits for the child to complete
before attempting to even connect to the object.

:author: Gregory Bell
:date: 3/7/23
"""

import multiprocessing
import multiprocessing.shared_memory
import sys
import unittest
from io import StringIO

import dill

from common import Runner, PossibleResults


class StudentSubmissionProcess(multiprocessing.Process):
    """
    This class extends multiprocessing.Process to provide a simple way to run student submissions.
    This class runs the 'runner' that it receives from the parent in a separate process and shares all data collected
    (returns, stdout, and exceptions) with the parent who is able to unpack it. Currently, stderror is ignored.

    Depending on the platform the process will be spawned using either the 'fork' or 'spawn' methods.
    Windows only supports the 'spawn' method and the 'spawn' method is preferred on macOS. This is why we aren't using
    pipes; when a process is created via the 'spawn' method, a new interpreter is started which doesn't share resources
    in the same way that a child process created via the 'fork' method. Thus, pipes fail on non Linux platforms.

    The other option of using multiprocessing.Pipe was also considered, but it ran in to similar issues as the
    traditional pipe method. There is a way to make it work, but it would involve overriding the print function to
    utilize the Pipe.send function, but that was a whole host of edge cases that I did not want to consider and also
    seemed like an easy way to confuse students as to why their print function behaved weird in the autograder, but not
    on their computers.

    Please be aware that the data does not generally persist after the child is started as it is a whole new context on
    some platforms. So data must be shared via some other mechanism. I choose multiprocessing.shared_memory due to the
    limitations listed above.

    This class is designed to a one-size-fits-all type of approach for actually *running* student submissions as I
    wanted to avoid the hodgepodge of unmaintainable that was the original autograder while still affording the
    flexibility required by the classes that will utilize it.
    """
    def __init__(self, _runner: callable, _stdinSharedMemName: str, _stdoutSharedMemName: str, _otherDataMemName: str, timeout: int = 10):
        """
        This constructs a new student submission process with the name "Student Submission".

        :param _runner: The submission runner to be run in a new process. Can be any callable object (lamda, function,
        etc). If there is a return value it will be shared with the parent.

        :param _stdinSharedMemName: The shared memory name (see :ref:`multiprocessing.shared_memory`) for stdin. The
        data at this location is stored as a list and must be processed into a format understood by ``StringIO``. The
        data here must exist before the child is started.

        :param _stdoutSharedMemName: The shared memory name (see :ref:`multiprocessing.shared_memory`) for stdout. This
        is created by the child and will be connected to by the parent once the child exits.

        :param _otherDataMemName: The shared memory name (see :ref:`multiprocessing.shared_memory`) for exceptions and
        return values. This is created by the child and will be connected to by the parent once the child exits.

        :param timeout: The _timeout for join. Basically, it will wait *at most* this amount of time for the child to
        terminate. After this period passes, the child must be killed by the parent.
        """
        super().__init__(name="Student Submission")
        self.runner: callable = _runner
        self.stdinSharedMemName: str = _stdinSharedMemName
        self.stdoutSharedMemName: str = _stdoutSharedMemName
        self.otherDataMemName: str = _otherDataMemName
        self.timeout: int = timeout

    def _setup(self) -> None:
        """
        Sets up the child input output redirection. The stdin is read from the shared memory object defined in the parent
        with the name ``self.stdinSharedMemName``. The stdin is formatted with newlines so that ``StringIO`` is able to
        work with it.

        The shared stdin object is destroyed after reading and is cleaned up from disk.

        .. warning: The shared stdin object is not accessible after this runs.

        stdout is also redirected here, but because we don't care about its contents, we just overwrite it completely.
        """
        sharedStdin = multiprocessing.shared_memory.ShareableList(name=self.stdinSharedMemName)
        # Reformat the stdin so that we
        sys.stdin = StringIO("".join([line + "\n" for line in sharedStdin]))

        sys.stdout = StringIO()

        sharedStdin.shm.close()
        sharedStdin.shm.unlink()

    def _teardown(self, _stdout: StringIO, _exception: Exception | None, _returnValue: object | None) -> None:
        """
        This function tears down the process after the runner exits. It pickles the exceptions that were raised and the
        return values from the runner. They are stored in the shared memory with the name ``self.otherDataMemName``.

        stdout is passed in to its shared memory with the name ``self.stdoutSharedMemName``.

        This function uses the dill library for pickle-ing as it supports almost everything out of the box. This means
        that no special code is needed to handle even complex return types.

        Pickle-ing in python is just a fancy way of saying converting to string. Pickle-ing is a form of serialization,
        and is easily reversible.

        :param _stdout: The raw io from the stdout.
        :param _exception: Any exceptions that were thrown
        :param _returnValue: The return value from the function
        """

        # Pickle both the exceptions and the return value
        otherData: list[str] = [dill.dumps(_exception), dill.dumps(_returnValue)]

        sharedOtherData = multiprocessing.shared_memory.ShareableList(otherData, name=self.otherDataMemName)
        sharedOtherData.shm.close()

        # Need to go to top of the buffer to read
        _stdout.seek(0)
        sharedStdout = multiprocessing.shared_memory.ShareableList(_stdout.getvalue().splitlines(), name=self.stdoutSharedMemName)
        sharedStdout.shm.close()

    def run(self):
        self._setup()

        returnValue: object = None
        exception: Exception | None = None
        try:
            returnValue = self.runner()
        except RuntimeError as rt_er:
            exception = rt_er
        except Exception as g_ex:
            exception = g_ex

        self._teardown(sys.stdout, exception, returnValue)

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

    def __init__(self, _stdin: list[str], _runner: Runner, _timeout: int, _mocks: list[unittest.mock.Mock]):
        self.stdin: list[str] = _stdin
        self.stdout: StringIO = StringIO()
        self.stdoutSharedName = "sub_stdout"
        self.stdinSharedName = "sub_stdin"
        self.otherDataMemName = "sub_other"
        self.studentSubmissionProcess = StudentSubmissionProcess(
            _runner,
            self.stdinSharedName, self.stdoutSharedName, self.otherDataMemName,
            _timeout)

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
            # If a timeout occurred, we can't trust any of the data in the shared memory. So don't even bother trying to
            #  read it. Esp as the student already failed
            return

        capturedStdoutFromChild = multiprocessing.shared_memory.ShareableList(name=self.stdoutSharedName)
        for el in capturedStdoutFromChild:
            self.stdout.write(el + "\n")

        capturedStdoutFromChild.shm.close()
        capturedStdoutFromChild.shm.unlink()

        capturedOtherData = multiprocessing.shared_memory.ShareableList(name=self.otherDataMemName)
        self.exception = dill.loads(capturedOtherData[0])
        self.returnData = dill.loads(capturedOtherData[1])
        capturedOtherData.shm.close()
        capturedOtherData.shm.unlink()

    def getTimeoutOccurred(self) -> bool:
        return self.timeoutOccurred

    def getException(self) -> Exception:
        return self.exception

    def populateResults(self, _resultData: dict[PossibleResults, any]):
        pass
