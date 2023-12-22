import os
import shutil
import unittest
import unittest.mock as mock
from StudentSubmission import StudentSubmissionExecutor, StudentSubmission, RunnableStudentSubmission
from StudentSubmission.Runners import MainModuleRunner
from StudentSubmission.common import PossibleResults, MissingFunctionDefinition


class TestStudentSubmissionExecutor(unittest.TestCase):
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

        StudentSubmissionExecutor.resultData = {}

        if os.path.exists(self.PYTHON_PROGRAM_DIRECTORY):
            shutil.rmtree(self.PYTHON_PROGRAM_DIRECTORY)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.DATA_DIRECTORY)

    def testCreateSandbox(self):
        StudentSubmissionExecutor.setup(self.environment, self.runner)

        self.assertIn(os.path.basename(self.environment.SANDBOX_LOCATION), os.listdir("."))

    def testMoveFiles(self):
        self.environment.files = {
            os.path.basename(self.TEST_FILE_LOCATION): os.path.basename(self.TEST_FILE_LOCATION)
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        self.assertIn(os.path.basename(self.TEST_FILE_LOCATION), os.listdir(self.DATA_DIRECTORY))

        StudentSubmissionExecutor.setup(self.environment, self.runner)

        self.assertIn(os.path.basename(self.TEST_FILE_LOCATION), os.listdir(self.environment.SANDBOX_LOCATION))

    def testMoveFilesWithAlais(self):
        self.environment.files = {
            os.path.basename(self.TEST_FILE_LOCATION) : "this_is_alais.txt"
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        StudentSubmissionExecutor.setup(self.environment, self.runner)

        self.assertIn("this_is_alais.txt", os.listdir(self.environment.SANDBOX_LOCATION))


        runnableSubmission = mock.Mock(spec=RunnableStudentSubmission.RunnableStudentSubmission)
        runnableSubmission.getOutputData = mock.Mock(return_value={})

        StudentSubmissionExecutor.postRun(self.environment, runnableSubmission)

        self.assertEqual({PossibleResults.FILE_OUT: {}, PossibleResults.FILE_HASH: {}}, self.environment.resultData)
        

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
                "\n"
                "raise Exception()\n"
            )

        self.environment.submission.getStudentSubmissionCode = lambda: compile(program, "test_code", "exec")

        with self.assertRaises(AssertionError):
            StudentSubmissionExecutor.execute(self.environment, self.runner)

    def testGeneratedFiles(self):
        runnableSubmission = mock.Mock()
        runnableSubmission.getOutputData = lambda: {}

        self.environment.files = {
            os.path.basename(self.TEST_FILE_LOCATION): os.path.basename(self.TEST_FILE_LOCATION)
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        StudentSubmissionExecutor.setup(self.environment, self.runner)

        with open(self.OUTPUT_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        StudentSubmissionExecutor.postRun(self.environment, runnableSubmission)

        self.assertIn(PossibleResults.FILE_OUT, self.environment.resultData.keys())

        expectedResults = {
            PossibleResults.FILE_OUT: {
                os.path.basename(self.OUTPUT_FILE_LOCATION): self.OUTPUT_FILE_LOCATION
            },
            PossibleResults.FILE_HASH: {
                os.path.basename(self.OUTPUT_FILE_LOCATION): "f5e55a898d1b68d6ad45f57fbf2cd0ed"

            }
        }

        self.assertDictEqual(self.environment.resultData, expectedResults)

    def testGetOrAssertFilePresent(self):
        expectedOutput = "this is a line in the file"

        os.mkdir(os.path.dirname(self.OUTPUT_FILE_LOCATION))

        with open(self.OUTPUT_FILE_LOCATION, 'w') as w:
            w.write(expectedOutput)

        self.environment.resultData = {
            PossibleResults.FILE_OUT: {
                os.path.basename(self.OUTPUT_FILE_LOCATION): self.OUTPUT_FILE_LOCATION
            }
        }

        actualOutput = StudentSubmissionExecutor \
            .getOrAssert(self.environment, PossibleResults.FILE_OUT, file=os.path.basename(self.OUTPUT_FILE_LOCATION))

        self.assertEqual(expectedOutput, actualOutput)

    def testGetOrAssertFileNotPresent(self):
        self.environment.resultData = {
            PossibleResults.FILE_OUT: {}
        }

        with self.assertRaises(AssertionError):
            StudentSubmissionExecutor \
                .getOrAssert(self.environment, PossibleResults.FILE_OUT,
                             file=os.path.basename(self.OUTPUT_FILE_LOCATION))

    def testGetOrAssertMockPresent(self):
        self.environment.resultData = {
            PossibleResults.MOCK_SIDE_EFFECTS: {
                "mock": mock.Mock()
            }
        }

        actualMock = StudentSubmissionExecutor.getOrAssert(self.environment, PossibleResults.MOCK_SIDE_EFFECTS,
                                                           mock="mock")

        self.assertIsNotNone(actualMock)

    def testGetOrAssertEmptyStdout(self):
        self.environment.resultData = {
            PossibleResults.STDOUT: []
        }

        with self.assertRaises(AssertionError):
            StudentSubmissionExecutor.getOrAssert(self.environment, PossibleResults.STDOUT)

    def testEOFError(self):
        actual = StudentSubmissionExecutor._processException(EOFError())

        self.assertIn("missing if __name__ == '__main__'", actual)


    def testMissingFunctionDefinition(self):
        functionName = "func1"
        actual = StudentSubmissionExecutor._processException(MissingFunctionDefinition(functionName))

        self.assertIn(functionName, actual)
        self.assertIn("missing the function definition", actual)
        self.assertEqual(actual.count("missing the function definition"), 1)


    def testSandboxNotCreatedCleanup(self):
        exception = None
        try:
            StudentSubmissionExecutor.cleanup(self.environment)
        except Exception as e:
            exception = e

        self.assertIsNone(exception)
        
    
