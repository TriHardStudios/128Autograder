import unittest
import os

from gradescope_utils.autograder_utils.decorators import weight

from Executors.Executor import Executor
from Executors.Environment import ExecutionEnvironmentBuilder, getOrAssert, PossibleResults
from StudentSubmissionImpl.C.CSubmission import CSubmission
from utils.config.Config import AutograderConfigurationProvider
from StudentSubmissionImpl.C.CRunners import MainRunner

class CHelloWorldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.autograderConfig = AutograderConfigurationProvider.get()

        if cls.autograderConfig.config.c is None:
            raise EnvironmentError("Missing C config")

        cls.studentSubmission = CSubmission(cls.autograderConfig.config.c.submission_name)\
                .setSubmissionRoot(cls.autograderConfig.config.student_submission_directory)\
                .load()\
                .build()\
                .validate()

    
    @weight(10)
    def testOutput(self):
        stdin = ["Hello C/C++/C-Like!"]
        environment = ExecutionEnvironmentBuilder(self.studentSubmission)\
                .setStdin(stdin)\
                .build()

        Executor.execute(environment, MainRunner())

        actualOutput = getOrAssert(environment, PossibleResults.STDOUT)

        self.assertEqual(stdin, actualOutput)
