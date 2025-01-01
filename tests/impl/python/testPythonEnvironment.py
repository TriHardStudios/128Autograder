import unittest
from lib.Executors.Environment import ExecutionEnvironment, Results, getResults

from lib.StudentSubmissionImpl.Python.PythonEnvironment import PythonEnvironment, PythonResults
from lib.TestingFramework import SingleFunctionMock

class TestPythonEnvironmentGetResults(unittest.TestCase):
    def setUp(self) -> None:
        self.environment = ExecutionEnvironment[PythonEnvironment, PythonResults]()

    def testGetOrAssertMockPresent(self):
        pythonResults = PythonResults(mocks={"mock": SingleFunctionMock("Mock")})

        self.environment.resultData = Results[PythonResults](impl_results=pythonResults)

        actualMock = getResults(self.environment).impl_results.mocks["mock"]

        self.assertIsNotNone(actualMock)
