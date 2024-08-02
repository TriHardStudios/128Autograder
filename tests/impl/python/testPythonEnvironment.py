import unittest
from Executors.Environment import ExecutionEnvironment, Results, getResults

from StudentSubmissionImpl.Python.PythonEnvironment import PythonEnvironment, PythonResults
from TestingFramework.SingleFunctionMock import SingleFunctionMock

class TestPythonEnvironmentGetResults(unittest.TestCase):
    def setUp(self) -> None:
        self.environment = ExecutionEnvironment[PythonEnvironment, PythonResults]()

    def testGetOrAssertMockPresent(self):
        pythonResults = PythonResults(mocks={"mock": SingleFunctionMock("Mock")})

        self.environment.resultData = Results[PythonResults](impl_results=pythonResults)

        actualMock = getResults(self.environment).impl_results.mocks["mock"]

        self.assertIsNotNone(actualMock)
