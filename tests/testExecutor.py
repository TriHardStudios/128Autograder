import shutil
from typing import Optional
import unittest
from unittest.mock import Mock
import os

from StudentSubmission.AbstractStudentSubmission import AbstractStudentSubmission
from StudentSubmission.ISubmissionProcess import ISubmissionProcess
from StudentSubmission.Runners import IRunner
from StudentSubmission.SubmissionProcessFactory import SubmissionProcessFactory
from StudentSubmission.common import MissingFunctionDefinition
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

    @unittest.skip("Imports are TBD and not really likely to be handled here")
    def testMoveFilesImports(self):
        with open(self.TEST_IMPORT_NAME, "w") as w:
            w.writelines("pass")

        self.environment.submission.getImports = \
            lambda: {self.TEST_IMPORT_NAME: os.path.basename(self.TEST_IMPORT_NAME)}

        StudentSubmissionExecutor.setup(self.environment, self.runner)

        self.assertIn(os.path.basename(self.TEST_IMPORT_NAME), os.listdir(self.environment.SANDBOX_LOCATION))

    def testExceptionRaised(self):
        program = \
            (
                "raise Exception()\n"
            )

        savedRun = MockRunner.run
        MockRunner.run = lambda self: exec(program)

        with self.assertRaises(AssertionError):
            Executor.execute(self.environment, self.runner)

        MockRunner.run = savedRun

    @unittest.skip("This will be handled by the 'populateResults' ")
    def testGeneratedFiles(self):
        self.environment.files = {
            self.TEST_FILE_LOCATION: self.OUTPUT_FILE_LOCATION
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        Executor.setup(self.environment, self.runner)

        with open(self.OUTPUT_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        Executor.postRun(self.environment, MockSubmissionProcess(), raiseExceptions=True)

        self.assertIn(PossibleResults.FILE_OUT, self.environment.resultData.keys())

        print(self.environment.resultData)
        expectedResults = {
            PossibleResults.FILE_OUT: {
                os.path.basename(self.OUTPUT_FILE_LOCATION): self.OUTPUT_FILE_LOCATION
            }
        }

        self.assertDictEqual(self.environment.resultData, expectedResults)


    @unittest.skip("This will be handled by the the python process")
    def testEOFError(self):
        actual = Executor._processException(EOFError())

        self.assertIn("missing if __name__ == '__main__'", actual)


    @unittest.skip("This will be handled the python process")
    def testMissingFunctionDefinition(self):
        functionName = "func1"
        actual = Executor._processException(MissingFunctionDefinition(functionName))

        self.assertIn(functionName, actual)
        self.assertIn("missing the function definition", actual)
        self.assertEqual(actual.count("missing the function definition"), 1)


    def testSandboxNotCreatedCleanup(self):
        exception = None
        try:
            Executor.cleanup(self.environment)
        except Exception as e:
            exception = e

        self.assertIsNone(exception)

