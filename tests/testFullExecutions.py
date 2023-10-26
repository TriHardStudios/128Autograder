import hashlib
import os
import shutil
import unittest
from unittest import mock

from StudentSubmission import StudentSubmissionExecutor, StudentSubmission
from StudentSubmission.Runners import MainModuleRunner
from StudentSubmission.common import PossibleResults


class TestFullExecutions(unittest.TestCase):
    DATA_DIRECTORY: str = "./testData"
    TEST_FILE_LOCATION: os.path = os.path.join(DATA_DIRECTORY, "testFile.txt")
    OUTPUT_FILE_LOCATION: os.path = os.path.join(
        StudentSubmissionExecutor.ExecutionEnvironment.SANDBOX_LOCATION,
        "outputFile.txt"
    )
    PYTHON_PROGRAM_DIRECTORY: str = "./testPrograms"
    TEST_IMPORT_NAME: os.path = os.path.join(PYTHON_PROGRAM_DIRECTORY, "mod1.py")

    @classmethod
    def setUpClass(cls) -> None:
        StudentSubmissionExecutor.dataDirectory = cls.DATA_DIRECTORY
        if os.path.exists(cls.DATA_DIRECTORY):
            shutil.rmtree(cls.DATA_DIRECTORY)
        os.mkdir(cls.DATA_DIRECTORY)

    def setUp(self) -> None:
        self.submission: mock = mock.Mock(spec_set=StudentSubmission)
        self.submission.getImports = lambda: None
        self.runner: MainModuleRunner = MainModuleRunner()

        self.environment: StudentSubmissionExecutor.ExecutionEnvironment = \
            StudentSubmissionExecutor.generateNewExecutionEnvironment(self.submission)

        if os.path.exists(self.PYTHON_PROGRAM_DIRECTORY):
            shutil.rmtree(self.PYTHON_PROGRAM_DIRECTORY)

        os.mkdir(self.PYTHON_PROGRAM_DIRECTORY)

    def tearDown(self) -> None:
        if "sandbox" in os.listdir("."):
            shutil.rmtree("sandbox")

        if os.path.exists(self.PYTHON_PROGRAM_DIRECTORY):
            shutil.rmtree(self.PYTHON_PROGRAM_DIRECTORY)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.DATA_DIRECTORY)

    def testFileIOFullExecution(self):
        # Because file io relies on the sandbox that the executor creates
        #  I am testing it as part of the executor tests

        expectedOutput = "this is a line in the file"
        program = \
            (
                f"fileContents = None\n"
                f"with open('{os.path.basename(self.TEST_FILE_LOCATION)}', 'r') as r:\n"
                f"    fileContents = r.read()\n"
                f"with open('{os.path.basename(self.OUTPUT_FILE_LOCATION)}', 'w') as w:\n"
                f"     w.write(fileContents)\n"
            )

        self.environment.submission.getStudentSubmissionCode = lambda: compile(program, "test_code", "exec")

        self.environment.files = {
            os.path.basename(self.TEST_FILE_LOCATION): os.path.basename(self.TEST_FILE_LOCATION)
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write(expectedOutput)

        StudentSubmissionExecutor.execute(self.environment, self.runner)
        actualOutput = StudentSubmissionExecutor \
            .getOrAssert(self.environment, PossibleResults.FILE_OUT, file=os.path.basename(self.OUTPUT_FILE_LOCATION))

        self.assertEqual(expectedOutput, actualOutput)

    def testImportFullExecution(self):
        # Because imports rely on the executor to move the files over,
        #  I am testing as part of the executor tests

        expectedOutput = "Called from a different file!!"
        with open(self.TEST_IMPORT_NAME, 'w') as w:
            w.writelines("def fun1():\n"
                         f"  print('OUTPUT {expectedOutput}')\n"
                         "\n")

        program = \
            (
                "from mod1 import fun1\n"
                "fun1()\n"
            )

        self.environment.submission.getImports = \
            lambda: {self.TEST_IMPORT_NAME: os.path.basename(self.TEST_IMPORT_NAME)}

        self.environment.submission.getStudentSubmissionCode = lambda: compile(program, "test_code", "exec")

        StudentSubmissionExecutor.execute(self.environment, self.runner)

        actualOutput = StudentSubmissionExecutor.getOrAssert(self.environment, PossibleResults.STDOUT)

        self.assertEqual(expectedOutput, actualOutput[0])


    def testExceptionRaisedResultPopulated(self):
        expectedOutput = "Huzzah"
        program = \
            (
                f"print('OUTPUT {expectedOutput}')\n"
                "raise Exception()"
            )

        self.environment.submission.getStudentSubmissionCode = lambda: compile(program, "test_code", "exec")
        
        with self.assertRaises(AssertionError):
            StudentSubmissionExecutor.execute(self.environment, self.runner)

        stdout = StudentSubmissionExecutor.getOrAssert(self.environment, PossibleResults.STDOUT)[0]
        exception = StudentSubmissionExecutor.getOrAssert(self.environment, PossibleResults.EXCEPTION)

        self.assertEqual(expectedOutput, stdout)
        self.assertIsInstance(exception, Exception)

    def testFileHashFullExecution(self):
        fileContents = "This is the contents of the file\n"

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write(fileContents)

        expectedFileHash = ""
        with open(self.TEST_FILE_LOCATION, 'rb') as rb:
            expectedFileHash = hashlib.md5(rb.read(), usedforsecurity=False).hexdigest()

        self.assertNotEqual(expectedFileHash, "")

        program = \
            (
                f"fileContents = None\n"
                f"with open('{os.path.basename(self.TEST_FILE_LOCATION)}', 'r') as r:\n"
                f"    fileContents = r.read()\n"
                f"with open('{os.path.basename(self.OUTPUT_FILE_LOCATION)}', 'w') as w:\n"
                f"     w.write(fileContents)\n"
            )

        self.environment.files = {
            os.path.basename(self.TEST_FILE_LOCATION): os.path.basename(self.TEST_FILE_LOCATION)
        }

        self.environment.submission.getStudentSubmissionCode = lambda: compile(program, "test_code", "exec")

        StudentSubmissionExecutor.execute(self.environment, self.runner)

        actualFileHash = StudentSubmissionExecutor.getOrAssert(self.environment, PossibleResults.FILE_HASH, file=os.path.basename(self.OUTPUT_FILE_LOCATION))

        self.assertEqual(expectedFileHash, actualFileHash)

        



