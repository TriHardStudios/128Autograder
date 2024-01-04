import unittest
from gradescope_utils.autograder_utils.decorators import weight

from Executors.Executor import Executor
from Executors.Environment import ExecutionEnvironmentBuilder, getOrAssert, PossibleResults
from StudentSubmissionImpl.Python.PythonSubmission import PythonSubmission
from utils.config.Config import AutograderConfigurationProvider
from StudentSubmissionImpl.Python.PythonRunners import MainModuleRunner


class HelloWorld(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.autograderConfig = AutograderConfigurationProvider.get()

        cls.studentSubmission = PythonSubmission()\
                .setSubmissionRoot(cls.autograderConfig.config.student_submission_directory)\
                .enableLooseMainMatching()\
                .load()\
                .build()

    def setUp(self) -> None:
        self.runner = MainModuleRunner()
        self.environmentBuilder = ExecutionEnvironmentBuilder(self.studentSubmission)

    @weight(10)
    def testCode(self):
        environment = self.environmentBuilder.build()


        Executor.execute(environment, self.runner)

        actualOutput = getOrAssert(environment, PossibleResults.STDOUT)

        self.assertEqual("Hello World", actualOutput[0])
