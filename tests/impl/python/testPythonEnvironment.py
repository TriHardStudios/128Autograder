import unittest
from StudentSubmission.AbstractStudentSubmission import AbstractStudentSubmission
from Executors.Environment import ExecutionEnvironment, Results, getResults

from StudentSubmissionImpl.Python.PythonEnvironment import PythonEnvironment, PythonResults
from TestingFramework.SingleFunctionMock import SingleFunctionMock

class MockSubmission(AbstractStudentSubmission[str]):
    def __init__(self):
        super().__init__()

    def doLoad(self):
       pass

    def doBuild(self):
        pass

    def getExecutableSubmission(self) -> str:
        return "Code!"

class TestPythonEnvironmentGetResults(unittest.TestCase):
    def setUp(self) -> None:
        self.environment = ExecutionEnvironment[PythonEnvironment, PythonResults](MockSubmission())

    def testGetOrAssertMockPresent(self):
        pythonResults = PythonResults(mocks={"mock": SingleFunctionMock("Mock")})

        self.environment.resultData = Results[PythonResults](impl_results=pythonResults)

        actualMock = getResults(self.environment).impl_results.mocks["mock"]

        self.assertIsNotNone(actualMock)
