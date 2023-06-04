import os
import shutil
import unittest
import unittest.mock as mock
from StudentSubmission import StudentSubmissionExecutor, StudentSubmission
from StudentSubmission.Runners import MainModuleRunner
from StudentSubmission.common import PossibleResults


class TestStudentSubmissionExecutor(unittest.TestCase):
    DATA_DIRECTORY: str = "./testData"
    TEST_FILE_LOCATION: os.path = os.path.join(DATA_DIRECTORY, "testFile.txt")
    OUTPUT_FILE_LOCATION: os.path = os.path.join(
        StudentSubmissionExecutor.ExecutionEnvironment.SANDBOX_LOCATION,
        "outputFile.txt"
    )

    @classmethod
    def setUpClass(cls) -> None:
        StudentSubmissionExecutor.dataDirectory = cls.DATA_DIRECTORY
        os.mkdir(cls.DATA_DIRECTORY)

    def setUp(self) -> None:
        self.submission: mock = mock.Mock(spec_set=StudentSubmission)
        self.runner: MainModuleRunner = MainModuleRunner()

        self.environment: StudentSubmissionExecutor.ExecutionEnvironment = \
            StudentSubmissionExecutor.generateNewExecutionEnvironment(self.submission)

    def tearDown(self) -> None:
        if "sandbox" in os.listdir("."):
            shutil.rmtree("sandbox")

        StudentSubmissionExecutor.resultData = {}

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.DATA_DIRECTORY)

    def testCreateSandbox(self):
        StudentSubmissionExecutor._setup(self.environment, self.runner)

        self.assertIn("sandbox", os.listdir("."))

    def testMoveFiles(self):
        self.environment.files = {
            os.path.basename(self.TEST_FILE_LOCATION): os.path.basename(self.TEST_FILE_LOCATION)
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        self.assertIn(os.path.basename(self.TEST_FILE_LOCATION), os.listdir(self.DATA_DIRECTORY))

        StudentSubmissionExecutor._setup(self.environment, self.runner)

        self.assertIn(os.path.basename(self.TEST_FILE_LOCATION), os.listdir(self.environment.SANDBOX_LOCATION))

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

        StudentSubmissionExecutor._setup(self.environment, self.runner)

        with open(self.OUTPUT_FILE_LOCATION, 'w') as w:
            w.write("this is a line in the file")

        StudentSubmissionExecutor._postRun(self.environment, runnableSubmission)

        self.assertIn(PossibleResults.FILE_OUT, StudentSubmissionExecutor.resultData.keys())

        expectedResults = {
            PossibleResults.FILE_OUT: {
                os.path.basename(self.OUTPUT_FILE_LOCATION): self.OUTPUT_FILE_LOCATION
            }
        }

        self.assertDictEqual(StudentSubmissionExecutor.resultData, expectedResults)

    def testGetOrAssertFilePresent(self):
        expectedOutput = "this is a line in the file"

        os.mkdir(os.path.dirname(self.OUTPUT_FILE_LOCATION))

        with open(self.OUTPUT_FILE_LOCATION, 'w') as w:
            w.write(expectedOutput)

        StudentSubmissionExecutor.resultData = {
            PossibleResults.FILE_OUT: {
                os.path.basename(self.OUTPUT_FILE_LOCATION): self.OUTPUT_FILE_LOCATION
            }
        }

        actualOutput = StudentSubmissionExecutor \
            .getOrAssert(PossibleResults.FILE_OUT, file=os.path.basename(self.OUTPUT_FILE_LOCATION))

        self.assertEqual(expectedOutput, actualOutput)

    def testGetOrAssertFileNotPresent(self):
        StudentSubmissionExecutor.resultData = {
            PossibleResults.FILE_OUT: {}
        }

        with self.assertRaises(AssertionError):
            StudentSubmissionExecutor \
                .getOrAssert(PossibleResults.FILE_OUT, file=os.path.basename(self.OUTPUT_FILE_LOCATION))

    def testGetOrAssertMockPresent(self):
        StudentSubmissionExecutor.resultData = {
            PossibleResults.MOCK_SIDE_EFFECTS: {
                "mock": mock.Mock()
            }
        }

        actualMock = StudentSubmissionExecutor.getOrAssert(PossibleResults.MOCK_SIDE_EFFECTS, mock="mock")

        self.assertIsNotNone(actualMock)

    def testFileIOFullExecution(self):
        # Because file io relies on the sandbox that the executor creates
        #  I am testing it as part of the executor tests

        expectedOutput = "this is a line in the file"
        program = \
            (
                f"fileContents = open('{os.path.basename(self.TEST_FILE_LOCATION)}').read()\n"
                f"open('{os.path.basename(self.OUTPUT_FILE_LOCATION)}', 'w').write(fileContents)\n"
            )

        self.environment.submission.getStudentSubmissionCode = lambda: compile(program, "test_code", "exec")

        self.environment.files = {
            os.path.basename(self.TEST_FILE_LOCATION): os.path.basename(self.TEST_FILE_LOCATION)
        }

        with open(self.TEST_FILE_LOCATION, 'w') as w:
            w.write(expectedOutput)

        StudentSubmissionExecutor.execute(self.environment, self.runner)
        actualOutput = StudentSubmissionExecutor \
            .getOrAssert(PossibleResults.FILE_OUT, file=os.path.basename(self.OUTPUT_FILE_LOCATION))

        self.assertEqual(expectedOutput, actualOutput)



