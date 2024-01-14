import unittest
from gradescope_utils.autograder_utils.decorators import weight

from Executors.Executor import Executor
from Executors.Environment import ExecutionEnvironmentBuilder, getOrAssert, PossibleResults
from StudentSubmissionImpl.Python.PythonSubmission import PythonSubmission
from utils.config.Config import AutograderConfigurationProvider
from StudentSubmissionImpl.Python.PythonRunners import MainModuleRunner


class RequirementsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.autograderConfig = AutograderConfigurationProvider.get()

        cls.studentSubmission = PythonSubmission()\
                .setSubmissionRoot(cls.autograderConfig.config.student_submission_directory)\
                .enableRequirements()\
                .load()\
                .build()\
                .validate()

    def setUp(self) -> None:
        self.runner = MainModuleRunner()
        self.environmentBuilder = ExecutionEnvironmentBuilder(self.studentSubmission)

    @weight(10)
    def testCode(self):
        environment = self.environmentBuilder.build()

        Executor.execute(environment, self.runner)

        actualOutput = getOrAssert(environment, PossibleResults.STDOUT)

        self.assertEqual(1, len(actualOutput)) # type: ignore

        
