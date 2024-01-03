import os
import shutil
import unittest

from Executors.Executor import Executor
from Executors.Environment import ExecutionEnvironmentBuilder, ExecutionEnvironment, PossibleResults, getOrAssert
from StudentSubmission.Runners import MainModuleRunner
from StudentSubmissionImpl.Python.PythonSubmission import PythonSubmission


# These serve as integration tests for the entire submission pipeline sans the gradescope stuff
class TestFullExecutions(unittest.TestCase):
    DATA_DIRECTORY: str = "./testData"
    TEST_FILE_NAME = "testFile.txt"
    OUTPUT_FILE_NAME = "outputFile.txt"

    PYTHON_PROGRAM_DIRECTORY: str = "./testPrograms"
    TEST_IMPORT_NAME = os.path.join(PYTHON_PROGRAM_DIRECTORY, "mod1.py")

    @classmethod
    def setUpClass(cls) -> None:
        from StudentSubmissionImpl.Python.PythonSubmissionProcess import RunnableStudentSubmission
        from StudentSubmission.SubmissionProcessFactory import SubmissionProcessFactory
        # This will need to be handled a bit differently imo
        SubmissionProcessFactory.register(PythonSubmission, RunnableStudentSubmission)

    def setUp(self) -> None:
        self.runner: MainModuleRunner = MainModuleRunner()

        if os.path.exists(self.DATA_DIRECTORY):
            shutil.rmtree(self.DATA_DIRECTORY)
        os.mkdir(self.DATA_DIRECTORY)

        if os.path.exists(self.PYTHON_PROGRAM_DIRECTORY):
            shutil.rmtree(self.PYTHON_PROGRAM_DIRECTORY)

        os.mkdir(self.PYTHON_PROGRAM_DIRECTORY)

    def tearDown(self) -> None:
        if os.path.exists(self.DATA_DIRECTORY):
            shutil.rmtree(self.DATA_DIRECTORY)

        if os.path.exists(ExecutionEnvironment.SANDBOX_LOCATION):
            shutil.rmtree(ExecutionEnvironment.SANDBOX_LOCATION)

        if os.path.exists(self.PYTHON_PROGRAM_DIRECTORY):
            shutil.rmtree(self.PYTHON_PROGRAM_DIRECTORY)


    @classmethod
    def writePythonFile(cls, filename, contents):
        path = os.path.join(cls.PYTHON_PROGRAM_DIRECTORY, filename)
        with open(path, 'w') as w:
            w.write(contents)

    def testFileIOFullExecution(self):
        # Because file io relies on the sandbox that the executor creates
        #  I am testing it as part of the executor tests

        expectedOutput = "this is a line in the file"
        program = \
                f"fileContents = None\n"\
                f"with open('{self.TEST_FILE_NAME}', 'r') as r:\n"\
                f"    fileContents = r.read()\n"\
                f"with open('{os.path.basename(self.OUTPUT_FILE_NAME)}', 'w') as w:\n"\
                f"     w.write(fileContents)\n"

        with open(os.path.join(self.DATA_DIRECTORY, self.TEST_FILE_NAME), 'w') as w:
            w.write(expectedOutput)

        self.writePythonFile("test_code.py", program)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.PYTHON_PROGRAM_DIRECTORY)\
                .enableLooseMainMatching()\
                .load()\
                .build()\
                .validate()

        environment = ExecutionEnvironmentBuilder(submission)\
                .setDataRoot(self.DATA_DIRECTORY)\
                .addFile(self.TEST_FILE_NAME, self.TEST_FILE_NAME)\
                .build()

        Executor.execute(environment, self.runner)

        actualOutput = getOrAssert(environment, PossibleResults.FILE_OUT, file=self.OUTPUT_FILE_NAME)

        self.assertEqual(expectedOutput, actualOutput)

    @unittest.skip("This will be implmeneted once imports are supported")
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

    @unittest.skip("This will be implmeneted once imports are supported")
    def testImportFullExecutionWithDataFiles(self):
        # Huge shout out to Nate T from F23 for finding this issue.
        # What a wild corner case

        expectedFileContents = "Called from a different file!!"
        testFileName = "test.txt"
        with open(self.TEST_IMPORT_NAME, 'w') as w:
            w.writelines("def fun1():\n"
                         f"  with open('{testFileName}', 'w') as w:\n"
                         f"    w.write('{expectedFileContents}')\n"
                         "\n")
        program = \
            (
                "from mod1 import fun1\n"
                "fun1()\n"
            )

        self.environment.submission.getImports = \
            lambda: {self.TEST_IMPORT_NAME: os.path.basename(self.TEST_IMPORT_NAME)}

        self.environment.files = {}

        self.environment.submission.getStudentSubmissionCode = lambda: compile(program, "test_code", "exec")

        StudentSubmissionExecutor.execute(self.environment, self.runner)

        actualOutput = StudentSubmissionExecutor.getOrAssert(self.environment, PossibleResults.FILE_OUT, file=testFileName)

        self.assertEqual(expectedFileContents, actualOutput)

    def testExceptionRaisedResultPopulated(self):
        expectedOutput = "Huzzah"
        program = \
                f"print('OUTPUT {expectedOutput}')\n"\
                "raise Exception()"

        self.writePythonFile("test_code.py", program)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.PYTHON_PROGRAM_DIRECTORY)\
                .enableLooseMainMatching()\
                .load()\
                .build()\
                .validate()

        environment = ExecutionEnvironmentBuilder(submission).build()

        with self.assertRaises(AssertionError):
            Executor.execute(environment, self.runner)

        stdout = getOrAssert(environment, PossibleResults.STDOUT)[0]
        exception = getOrAssert(environment, PossibleResults.EXCEPTION)

        self.assertEqual(expectedOutput, stdout)
        self.assertIsInstance(exception, Exception)


