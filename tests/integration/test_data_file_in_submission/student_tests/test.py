import unittest
import os
from gradescope_utils.autograder_utils.decorators import weight

from Executors.Executor import Executor
from Executors.Environment import ExecutionEnvironmentBuilder, getOrAssert, PossibleResults
from StudentSubmissionImpl.Python.PythonSubmission import PythonSubmission
from utils.config.Config import AutograderConfigurationProvider
from StudentSubmissionImpl.Python.PythonRunners import FunctionRunner


class DataFilesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.autograderConfig = AutograderConfigurationProvider.get()

        cls.studentSubmission = PythonSubmission()\
                .setSubmissionRoot(cls.autograderConfig.config.student_submission_directory)\
                .load()\
                .build()\
                .validate()

    def setUp(self) -> None:
        submissionDirectory = self.autograderConfig.config.student_submission_directory
        testFolder = os.path.join("autograder", "source", self.autograderConfig.config.test_directory, "data")

        self.environmentBuilder = ExecutionEnvironmentBuilder(self.studentSubmission)\
                .setDataRoot("/")

        self.environmentBuilder\
                .addFile(os.path.join(submissionDirectory, "file.dat"), "file.dat")\
                .addFile(os.path.join(testFolder, "public_file.dat"), "public_file.dat")


    @weight(5)
    def testSubmissionData(self):
        environment = self.environmentBuilder.build()

        runner = FunctionRunner("readFile", "file.dat")

        Executor.execute(environment, runner)

        actualOutput = getOrAssert(environment, PossibleResults.RETURN_VAL)

        self.assertEqual("file.dat", actualOutput)

    @weight(5)
    def testProvidedData(self):
        environment = self.environmentBuilder.build()

        runner = FunctionRunner("readFile", "public_file.dat")

        Executor.execute(environment, runner)

        actualOutput = getOrAssert(environment, PossibleResults.RETURN_VAL)

        self.assertEqual("public_file.dat", actualOutput)
