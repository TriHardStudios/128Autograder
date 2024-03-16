import os
import shutil
import unittest

from Executors.Executor import Executor
from Executors.Environment import ExecutionEnvironmentBuilder, ExecutionEnvironment, PossibleResults, getOrAssert
from StudentSubmissionImpl.Python.PythonFileImportFactory import PythonFileImportFactory
from StudentSubmissionImpl.Python.PythonRunners import FunctionRunner, MainModuleRunner
from StudentSubmissionImpl.Python.PythonSubmission import PythonSubmission


# These serve as integration tests for the entire submission pipeline sans the gradescope stuff
class TestFullExecutions(unittest.TestCase):
    DATA_DIRECTORY: str = "./testData"
    TEST_FILE_NAME = "testFile.txt"
    OUTPUT_FILE_NAME = "outputFile.txt"

    PYTHON_PROGRAM_DIRECTORY: str = "./testPrograms"
    TEST_IMPORT_NAME = os.path.join(PYTHON_PROGRAM_DIRECTORY, "mod1.py")

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

    def testExecutorSetsParameters(self):
        program = \
                "def fun(param, *args):\n"\
                "    return (param, *args)"

        self.writePythonFile("test_code.py", program)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.PYTHON_PROGRAM_DIRECTORY)\
                .enableLooseMainMatching()\
                .load()\
                .build()\
                .validate()

        environment = ExecutionEnvironmentBuilder(submission)\
                .addParameter(1)\
                .addParameter(2)\
                .addParameter(3)\
                .build()

        runner = FunctionRunner("fun")

        Executor.execute(environment, runner)

        actualOutput = getOrAssert(environment, PossibleResults.PARAMETERS)

        self.assertEqual(3, len(actualOutput)) # type: ignore
        self.assertEqual(3, actualOutput[2]) # type: ignore

    def testImportFullExecution(self):
        expectedOutput = 10
        with open(self.TEST_IMPORT_NAME, 'w') as w:
            w.writelines("def fun1():\n"
                         f"  return {expectedOutput}\n"
                         "\n")
        with open(os.path.join(self.PYTHON_PROGRAM_DIRECTORY, "main.py"), 'w') as w:
            w.writelines(
                "from mod1 import fun1\n"\
                "def run():\n"\
                "    return fun1()\n"
            )

        submission = PythonSubmission()\
                .setSubmissionRoot(self.PYTHON_PROGRAM_DIRECTORY)\
                .load()\
                .build()\
                .validate()

        PythonFileImportFactory.registerFile(os.path.abspath(self.TEST_IMPORT_NAME), "mod1")

        importHandler = PythonFileImportFactory.buildImport()

        if importHandler is None:
            self.fail("This shouldn't happen")

        environment = ExecutionEnvironmentBuilder(submission)\
                .addImportHandler(importHandler)\
                .build()

        runner = FunctionRunner("run")

        Executor.execute(environment, runner)

        actualOutput = getOrAssert(environment, PossibleResults.RETURN_VAL)

        self.assertEqual(expectedOutput, actualOutput) # type: ignore

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
        with open(os.path.join(self.PYTHON_PROGRAM_DIRECTORY, "main.py"), 'w') as w:
            w.writelines(
                "from mod1 import fun1\n"\
                "fun1()\n"
            )

        submission = PythonSubmission()\
                .setSubmissionRoot(self.PYTHON_PROGRAM_DIRECTORY)\
                .load()\
                .build()\
                .validate()

        PythonImportFactory.registerFile(os.path.abspath(self.TEST_IMPORT_NAME), "mod1")
        importHandler = PythonImportFactory.buildImport()

        if importHandler is None:
            self.fail("This shouldn't happen")

        environment = ExecutionEnvironmentBuilder(submission)\
                .addImportHandler(importHandler)\
                .build()

        Executor.execute(environment, self.runner)

        actualOutput = getOrAssert(environment, PossibleResults.FILE_OUT, file=testFileName)

        self.assertEqual(expectedFileContents, actualOutput)

    def testImportWithFunction(self):
        expectedOutput = 10
        program = \
                "from mod1 import fun1\n"\
                "def run():\n"\
                "    return fun1()\n"

        with open(self.TEST_IMPORT_NAME, 'w') as w:
            w.writelines(
                "def fun1():\n"
                f"  return {expectedOutput}"
                "\n"
            )

        self.writePythonFile("main.py", program)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.PYTHON_PROGRAM_DIRECTORY)\
                .load()\
                .build()\
                .validate()

        PythonImportFactory.registerFile(os.path.abspath(self.TEST_IMPORT_NAME), "mod1")
        PythonImportFactory.registerFile(os.path.abspath(os.path.join(self.PYTHON_PROGRAM_DIRECTORY, "main.py")), "main")
        importHandler = PythonImportFactory.buildImport()

        if importHandler is None:
            self.fail("This shouldn't happen")

        environment = ExecutionEnvironmentBuilder(submission)\
                .addImportHandler(importHandler)\
                .build()

        runner = FunctionRunner("run")

        Executor.execute(environment, runner)

        actualOutput = getOrAssert(environment, PossibleResults.RETURN_VAL)

        self.assertEqual(expectedOutput, actualOutput) # type: ignore


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

        stdout = getOrAssert(environment, PossibleResults.STDOUT)[0] # type: ignore
        exception = getOrAssert(environment, PossibleResults.EXCEPTION)

        self.assertEqual(expectedOutput, stdout)
        self.assertIsInstance(exception, Exception)


