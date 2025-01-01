import unittest
from autograder_utils.Decorators import Weight

from lib.Executors.Executor import Executor
from lib.Executors.Environment import ExecutionEnvironmentBuilder, getResults
from lib.StudentSubmissionImpl.Python import PythonSubmission
from lib.config import AutograderConfigurationProvider
from lib.StudentSubmissionImpl.Python.Runners import PythonRunnerBuilder


class HelloWorld(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.autograderConfig = AutograderConfigurationProvider.get()

        cls.studentSubmission = PythonSubmission() \
            .setSubmissionRoot(cls.autograderConfig.config.student_submission_directory) \
            .enableLooseMainMatching() \
            .load() \
            .build()

    def setUp(self) -> None:
        self.environmentBuilder = ExecutionEnvironmentBuilder()

    @Weight(10)
    def testCode(self):
        environment = self.environmentBuilder.build()

        runner = PythonRunnerBuilder(self.studentSubmission) \
            .setEntrypoint(module=True) \
            .build()

        Executor.execute(environment, runner)

        actualOutput = getResults(environment).stdout

        self.assertEqual("Hello World", actualOutput[0])
