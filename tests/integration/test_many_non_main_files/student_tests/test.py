import unittest
from gradescope_utils.autograder_utils.decorators import weight

from Executors.Executor import Executor
from Executors.Environment import ExecutionEnvironmentBuilder, getResults
from StudentSubmissionImpl.Python.PythonSubmission import PythonSubmission
from utils.config.Config import AutograderConfigurationProvider
from StudentSubmissionImpl.Python.Runners import PythonRunnerBuilder

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
        self.environmentBuilder = ExecutionEnvironmentBuilder()

    @weight(10)
    def testCode(self):
        environment = self.environmentBuilder.build()

        runner = PythonRunnerBuilder(self.studentSubmission)\
            .setEntrypoint(module=True)\
            .build()

        Executor.execute(environment, runner)

        actualOutput = getResults(environment).stdout

        self.assertEqual("Hello World", actualOutput[0])
