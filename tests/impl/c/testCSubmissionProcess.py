import unittest
from unittest.mock import MagicMock
import subprocess
import os
import shutil

from Executors.Environment import ExecutionEnvironment, PossibleResults
from StudentSubmissionImpl.C.CSubmissionProcess import CSubmissionProcess
from StudentSubmissionImpl.C.CRunners import MainRunner

class CSubmissionProcessTests(unittest.TestCase):
    SUBMISSION_LOCATION: str = "./test_files"
    EXEC_FILE_LOCATION: str = os.path.join(SUBMISSION_LOCATION, "execuable_file")

    @classmethod
    def setUpClass(cls) -> None:
        cls.subprocess = subprocess.Popen.__new__

    def setUp(self) -> None:
        self.environment = ExecutionEnvironment(None) # type: ignore
        self.submissionProcess = CSubmissionProcess()
        self.runner = MainRunner()
        self.runner.setSubmission(self.EXEC_FILE_LOCATION)

        self.mock = MagicMock()
        subprocess.Popen.__new__ = MagicMock()
        subprocess.Popen.__new__.return_value = self.mock

        if os.path.exists(self.environment.SANDBOX_LOCATION):
            shutil.rmtree(self.environment.SANDBOX_LOCATION)

        if os.path.exists(self.SUBMISSION_LOCATION):
            shutil.rmtree(self.SUBMISSION_LOCATION)

        os.mkdir(self.SUBMISSION_LOCATION)
        os.mkdir(self.environment.SANDBOX_LOCATION)

        with open(self.EXEC_FILE_LOCATION, "w") as w:
            w.write("")


    def tearDown(self) -> None:
        if os.path.exists(self.environment.SANDBOX_LOCATION):
            shutil.rmtree(self.environment.SANDBOX_LOCATION)

        if os.path.exists(self.SUBMISSION_LOCATION):
            shutil.rmtree(self.SUBMISSION_LOCATION)

        self.mock.reset_mock()

    @classmethod
    def tearDownClass(cls):
        del subprocess.Popen.__new__
        if subprocess.Popen.__new__ is not object.__new__:
            subprocess.Popen.__new__ = cls.subprocess
        else:
            subprocess.Popen.__new__ = lambda other, *args, **kw: object.__new__(other) # type: ignore


    def testMoveFileToSandbox(self):
        self.assertNotIn(os.path.basename(self.EXEC_FILE_LOCATION), os.listdir(self.environment.SANDBOX_LOCATION))

        self.submissionProcess.setup(self.environment, self.runner)

        self.assertIn(os.path.basename(self.EXEC_FILE_LOCATION), os.listdir(self.environment.SANDBOX_LOCATION))


    def testTimeoutProcessed(self):
        # This is kinda a weird test, we are relying that this library handle this correctly
        # so we are just setting the state that want
        self.environment.timeout = 1
        self.mock.communicate.side_effect = subprocess.TimeoutExpired("test", self.environment.timeout)

        self.submissionProcess.setup(self.environment, self.runner)
        self.submissionProcess.run()
        self.submissionProcess.cleanup()

        self.submissionProcess.populateResults(self.environment)

        with self.assertRaises(TimeoutError) as ex:
            raise self.environment.resultData[PossibleResults.EXCEPTION] # type: ignore

        exceptionText = str(ex.exception)

        self.assertIn(f"timed out after {self.environment.timeout}", exceptionText)


    def testStdout(self):
        self.environment.stdin = ["Huzzah!", "Output!"]

        self.mock.communicate = lambda stdin, timeout: (stdin, None) 

        self.submissionProcess.setup(self.environment, self.runner)
        self.submissionProcess.run()
        self.submissionProcess.cleanup()

        self.submissionProcess.populateResults(self.environment)
        
        self.submissionProcess.processAndRaiseExceptions(self.environment)

        self.assertEqual(self.environment.stdin, self.environment.resultData[PossibleResults.STDOUT])

    def testExceptionRaised(self):
        self.mock.communicate.side_effect = AttributeError("This is an exception raised by the child!")

        self.submissionProcess.setup(self.environment, self.runner)
        self.submissionProcess.run()
        self.submissionProcess.cleanup()

        self.submissionProcess.populateResults(self.environment)

        with self.assertRaises(AttributeError):
            raise self.environment.resultData[PossibleResults.EXCEPTION] # type: ignore

    def testExceptionRaisedDuringProcessCreation(self):
        subprocess.Popen.__new__.side_effect = OSError("The process totally failed to spawn") # type: ignore

        self.submissionProcess.setup(self.environment, self.runner)
        self.submissionProcess.run()
        self.submissionProcess.cleanup()

        self.submissionProcess.populateResults(self.environment)

        with self.assertRaises(EnvironmentError) as ex:
            raise self.environment.resultData[PossibleResults.EXCEPTION] # type: ignore

        exceptionText = str(ex.exception)

        self.assertIn("Failed to start student submission", exceptionText)

    def testFileIO(self):
        fileToCreate = os.path.join(self.environment.SANDBOX_LOCATION, "written_file.txt")
        with open(fileToCreate, 'w') as w:
            w.write("")

        self.submissionProcess.setup(self.environment, self.runner)
        self.submissionProcess.populateResults(self.environment)

        self.assertIn(os.path.basename(fileToCreate), self.environment.resultData[PossibleResults.FILE_OUT]) # type: ignore


    def testEOFError(self):
        self.mock.communicate.side_effect = EOFError()

        self.submissionProcess.setup(self.environment, self.runner)
        self.submissionProcess.run()
        self.submissionProcess.cleanup()

        self.submissionProcess.populateResults(self.environment)

        with self.assertRaises(AssertionError) as ex:
            self.submissionProcess.processAndRaiseExceptions(self.environment)

        exceptionText = str(ex.exception)

        self.assertIn("EOFError", exceptionText)
        self.assertIn("Do you have the correct number of input statements?", exceptionText)
