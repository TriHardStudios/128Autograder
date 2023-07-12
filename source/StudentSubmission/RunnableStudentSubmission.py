"""
This module provides an interface for running student submissions as processes.

This module utilizes shared memory to share data from the parent and the child. The way it is currently implemented
guarantees that no conflicts will occur with the pattern. This is because the parent waits for the child to complete
before attempting to even connect to the object.

:author: Gregory Bell
:date: 3/7/23
"""

import multiprocessing
import multiprocessing.shared_memory as shared_memory
import os
import sys
from io import StringIO

import dill

from StudentSubmission.common import PossibleResults
from StudentSubmission.Runners import Runner


SHARED_STDIN_NAME: str = "sub_stdin"
SHARED_STDOUT_NAME: str = "sub_stdout"
SHARED_GENERAL_NAME: str =  "sub_stdout"

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

    def __init__(self, _runner: Runner, _inputSharedMemName: str, _outputDataMemName: str,
                 _executionDirectory: str, timeout: int = 10):
        """
        This constructs a new student submission process with the name "Student Submission".

        :param _runner: The submission runner to be run in a new process. Can be any callable object (lamda, function,
        etc). If there is a return value it will be shared with the parent.

        :param _inputSharedMemName: The shared memory name (see :ref:`multiprocessing.shared_memory`) for stdin. The
        data at this location is stored as a list and must be processed into a format understood by ``StringIO``. The
        data here must exist before the child is started.

        :param _outputDataMemName: The shared memory name (see :ref:`multiprocessing.shared_memory`) for exceptions and
        return values. This is created by the child and will be connected to by the parent once the child exits.

        :param _executionDirectory: The directory that this process should be running in. This is to make sure that all
        data is isolated for each run of the autograder.

        :param timeout: The _timeout for join. Basically, it will wait *at most* this amount of time for the child to
        terminate. After this period passes, the child must be killed by the parent.
        """
        super().__init__(name="Student Submission")
        self.runner: Runner = _runner
        self.inputDataMemName: str = _inputSharedMemName
        self.outputDataMemName: str = _outputDataMemName
        self.executionDirectory: str = _executionDirectory
        self.timeout: int = timeout

    def _setup(self) -> None:
        """
        Sets up the child input output redirection. The stdin is read from the shared memory object defined in the parent
        with the name ``self.inputDataMemName``. The stdin is formatted with newlines so that ``StringIO`` is able to
        work with it.

        This method also moves the process to the execution directory

        stdout is also redirected here, but because we don't care about its contents, we just overwrite it completely.
        """
        os.chdir(self.executionDirectory)
        sys.path.append(os.getcwd())

        sharedInput = multiprocessing.shared_memory.SharedMemory(self.inputDataMemName)
        deserializedData = dill.loads(sharedInput.buf.tobytes())
        # Reformat the stdin so that we
        sys.stdin = StringIO("".join([line + "\n" for line in deserializedData]))

        sys.stdout = StringIO()

    def _teardown(self, _stdout: StringIO | None = None, _exception: Exception | None = None, _returnValue: object | None = None, _mocks: dict[str, object] | None = None) -> None:
        """
.       This function takes the results from the child process and serializes them.
        Then is stored in the shared memory object that the parent is able to access.

        :param _stdout: The raw io from the stdout.
        :param _exception: Any exceptions that were thrown
        :param _returnValue: The return value from the function
        :param _mocks: The mocks from the submission after they have been hydrated
        """

        # Pickle both the exceptions and the return value
        dataToSerialize: dict[PossibleResults, object] = {
            PossibleResults.STDOUT: _stdout.getvalue().splitlines(),
            PossibleResults.EXCEPTION: _exception,
            PossibleResults.RETURN_VAL: _returnValue,
            PossibleResults.MOCK_SIDE_EFFECTS: _mocks
        }

        serializedData = dill.dumps(dataToSerialize, dill.HIGHEST_PROTOCOL)
        sharedOutput = shared_memory.SharedMemory(self.outputDataMemName)

        sharedOutput.buf[:len(serializedData)] = serializedData
        sharedOutput.close()

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

        self._teardown(sys.stdout, exception, returnValue, self.runner.getMocks())

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

    def __init__(self, _stdin: list[str], _runner: Runner,  _executionDirectory: str, _timeout: int):
        self.stdin: list[str] = _stdin
        self.inputDataMemName = "input_data"
        self.outputDataMemName = "output_data"

        self.inputSharedMem: shared_memory.SharedMemory | None = None
        self.outputSharedMem: shared_memory.SharedMemory | None = None

        self.studentSubmissionProcess = StudentSubmissionProcess(
            _runner,
            self.inputDataMemName, self.outputDataMemName, _executionDirectory,
            _timeout)

        self.timeoutOccurred: bool = False
        self.exception: Exception | None = None
        self.outputData: dict[PossibleResults, object] = {}

    def setup(self, memorySize: int = 2 ** 20):
        """
        This function sets up the data that will be shared between the two processes.

        Setting up the data here then tearing it down in the ref:`RunnableStudentSubmission.cleanup` fixes
        the issue with windows GC cleaning up the memory before we are done with it as there will be at least one
        active hook for each memory resource til ``cleanup`` is called.

        :param memorySize: The amount of memory that should be allocated to each memory resource. Defaults to 1 MiB
        """

        self.inputSharedMem = shared_memory.SharedMemory(self.inputDataMemName, create=True, size=memorySize)
        self.outputSharedMem = shared_memory.SharedMemory(self.outputDataMemName, create=True, size=memorySize)
        
    def run(self):
        self.setup()

        # allocate 1 mb for the shared memory
        serializedStdin = dill.dumps(self.stdin, dill.HIGHEST_PROTOCOL)

        self.inputSharedMem.buf[:len(serializedStdin)] = serializedStdin

        self.studentSubmissionProcess.start()

        self.studentSubmissionProcess.join()

        if self.studentSubmissionProcess.is_alive():
            self.studentSubmissionProcess.terminate()
            self.timeoutOccurred = True
            # If a timeout occurred, we can't trust any of the data in the shared memory. So don't even bother trying to
            #  read it. Esp as the student already failed
            self.cleanup()
            return

        deserializedData: dict[PossibleResults, object] = dill.loads(self.outputSharedMem.buf.tobytes())

        self.exception = deserializedData[PossibleResults.EXCEPTION]
        self.outputData = deserializedData

        self.cleanup()

    def cleanup(self):
        """
        This function cleans up the shared memory object by closing the parent hook and then unlinking it.

        After it is unlinked, the python garbage collector cleans it up.
        On windows, the GC runs as soon as the last hook is closed and `unlink` is a noop
        """
        # `close` closes the current hook
        self.inputSharedMem.close()
        # `unlink` tells the gc that it is ok to clean up this resource
        #  On windows, `unlink` is a noop
        self.inputSharedMem.unlink()

        self.outputSharedMem.close()
        self.outputSharedMem.unlink()

    def getTimeoutOccurred(self) -> bool:
        return self.timeoutOccurred

    def getException(self) -> Exception:
        return self.exception

    def getOutputData(self) -> dict[PossibleResults, any]:
        return self.outputData
