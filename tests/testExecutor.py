import shutil
from typing import Optional, Tuple, Any
import unittest
import os

from StudentSubmission.AbstractStudentSubmission import AbstractStudentSubmission
from StudentSubmission.ISubmissionProcess import ISubmissionProcess
from StudentSubmission.Runners import IRunner
from StudentSubmission.SubmissionProcessFactory import SubmissionProcessFactory
from Executors.Executor import Executor
from Executors.Environment import ExecutionEnvironment,PossibleResults


class MockSubmission(AbstractStudentSubmission[str]):
    def __init__(self):
        super().__init__()
        self.studentCode: str = "No code"

    def doLoad(self):
        self.studentCode = "Loaded code!"

    def doBuild(self):
        self.studentCode = "Built code!"

    def getExecutableSubmission(self) -> str:
        return self.studentCode

class MockRunner(IRunner[str]):
    def __init__(self) -> None:
        self.code: str = ""

    def setSubmission(self, submission: str):
        self.code = submission

    def setParameters(self, parameters: Tuple[Any]):
        pass

    def run(self) -> Optional[str]:
        return self.code

    def __call__(self):
        return self.run()


class MockSubmissionProcess(ISubmissionProcess):
    def __init__(self):
        self.output = ""
        self.exceptions: Optional[Exception] = None
        self.runner: Optional[MockRunner] = None

    def setup(self, _, runner: MockRunner):
        self.runner = runner

    def run(self):
        if self.runner is None:
            return

        try:
            self.output = self.runner()
        except Exception as ex:
            self.exceptions = ex

    def populateResults(self, environment: ExecutionEnvironment):
        environment.resultData[PossibleResults.STDOUT] = self.output
        environment.resultData[PossibleResults.EXCEPTION] = self.exceptions

    def cleanup(self):
        pass

    @classmethod
    def processAndRaiseExceptions(cls, environment: ExecutionEnvironment):
        if environment.resultData[PossibleResults.EXCEPTION] is not None:
            raise AssertionError()


SubmissionProcessFactory.register(MockSubmission, MockSubmissionProcess)

class TestExecutor(unittest.TestCase):
    TEST_FILE_ROOT = "./test_data"
    TEST_FILE_LOCATION = os.path.join(TEST_FILE_ROOT, "sub", "test.txt")
    OUTPUT_FILE_LOCATION = os.path.join(ExecutionEnvironment.SANDBOX_LOCATION,
                                        os.path.basename(TEST_FILE_LOCATION))

    def setUp(self) -> None:
        os.makedirs(os.path.dirname(self.TEST_FILE_LOCATION), exist_ok=True)

        self.submission = MockSubmission().build()
        self.environment = ExecutionEnvironment(self.submission)
        self.runner = MockRunner()

    def tearDown(self) -> None:
        if os.path.exists(self.environment.SANDBOX_LOCATION):
            shutil.rmtree(self.environment.SANDBOX_LOCATION)

        if os.path.exists(self.TEST_FILE_ROOT):
            shutil.rmtree(self.TEST_FILE_ROOT)

    def testCreateSandbox(self):
        Executor.setup(self.environment, self.runner)

        self.assertIn(os.path.basename(self.environment.SANDBOX_LOCATION), os.listdir("."))

    def testMoveFiles(self):
        self.environment.files = {
            self.TEST_FILE_LOCATION: self.OUTPUT_FILE_LOCATION
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        Executor.setup(self.environment, self.runner)

        self.assertIn(os.path.basename(self.TEST_FILE_LOCATION), os.listdir(self.environment.SANDBOX_LOCATION))

    def testMoveFilesWithAlais(self):
        self.environment.files = {
            self.TEST_FILE_LOCATION :
                os.path.join(self.environment.SANDBOX_LOCATION, "this_is_alais.txt")
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        Executor.setup(self.environment, self.runner)

        self.assertIn("this_is_alais.txt", os.listdir(self.environment.SANDBOX_LOCATION))

    def testExceptionRaised(self):
        program = \
            (
                "raise Exception()\n"
            )

        savedRun = MockRunner.run
        MockRunner.run = lambda _: exec(program) # type: ignore

        with self.assertRaises(AssertionError):
            Executor.execute(self.environment, self.runner)

        MockRunner.run = savedRun

    def testSandboxNotCreatedCleanup(self):
        exception = None
        try:
            Executor.cleanup(self.environment)
        except Exception as e:
            exception = e

        self.assertIsNone(exception)

