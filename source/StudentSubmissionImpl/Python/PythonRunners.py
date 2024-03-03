import sys
from abc import abstractmethod
import importlib
from types import CodeType, ModuleType, FunctionType
from typing import Dict, List, Optional, Tuple, Any

from StudentSubmission.common import MissingFunctionDefinition, InvalidTestCaseSetupCode
from TestingFramework.SingleFunctionMock import SingleFunctionMock
from StudentSubmission.Runners import IRunner

# OMG I FINALLY FOUND HOW TO DO THIS CORRECTLY!!
# https://stackoverflow.com/questions/55905240/python-dynamically-import-modules-code-from-string-with-importlib
# https://docs.python.org/3/reference/import.html#the-meta-path
# https://stackoverflow.com/questions/43571737/how-to-implement-an-import-hook-that-can-modify-the-source-code-on-the-fly-using

class GenericPythonRunner(IRunner[CodeType]):
    """
    :Description:
    This class contains common code needed for each runner.

    A runner is a unit of execution that controls how the student's submission is executed.

    Child classes should implement ``Runner.run`` which is what is called at run time by
    ``RunnableStudentSubmissionProcess``.

    If mocks are supported by runner, then ``Runner.applyMocks`` should be called after the student is loaded into
    the current frame.
    """

    AUTOGRADER_SETUP_NAME: str = "autograder_setup"

    def __init__(self):
        self.studentSubmission: Optional[CodeType] = None
        self.mocks: Optional[Dict[str, SingleFunctionMock]] = None
        self.parameters: Tuple[Any] = tuple()
        self.setupCode = None

    def setSubmission(self, submission: CodeType):
        self.studentSubmission = submission

    def setParameters(self, parameters: Tuple[Any]):
        self.parameters = parameters

    def getParameters(self) -> Tuple[Any]:
        return self.parameters

    def setMocks(self, mocks: Dict[str, SingleFunctionMock]):
        self.mocks = mocks

    def getMocks(self) -> dict[str, SingleFunctionMock] | None:
        return self.mocks

    def setSetupCode(self, setupCode):
        self.setupCode = compile(setupCode, "setup_code", "exec")

    def applyMocks(self, module: ModuleType) -> None:
        """
        This function applies the mocks to the student's submission at the module level.

        :param module: the module to apply mocks to 

        :raises AttributeError: If a mock name cannot be resolved
        """
        if not self.mocks:
            return

        for mockName, mock in self.mocks.items():
            if mock.spy:
                mock.setSpyFunction(getattr(module, mockName))

            setattr(module, mockName, mock)

    @abstractmethod
    def run(self):
        raise NotImplementedError("Must use implementation of runner.")

    def __call__(self):
        return self.run()


class MainModuleRunner(GenericPythonRunner):
    def run(self):
        if self.studentSubmission == None:
            raise RuntimeError("INVALID STATE: Submission was NONE when should be a non-none type!")

        exec(self.studentSubmission, {'__name__': "__main__"})


class FunctionRunner(GenericPythonRunner):

    def __init__(self, functionToCall: str, submissionModules: Optional[List[str]] = None):

        super().__init__()
        if submissionModules is None:
            submissionModules = ["submission", "main"]

        self.functionToCall: str = functionToCall
        self.modulesToImport: List[str] = submissionModules

    def attemptToImport(self) -> ModuleType:
        importedModule: Optional[ModuleType] = None

        for moduleName in self.modulesToImport:
            try:
                importedModule = importlib.import_module(moduleName)
                importedModule = importlib.reload(importedModule)
            except ImportError:
                pass

        if importedModule is None:
            raise MissingFunctionDefinition(f"{self.modulesToImport}.{self.functionToCall}")

        return importedModule

    @staticmethod
    def getMethod(module: ModuleType, functionName: str):
        function = getattr(module, functionName, None)

        if function is None:
            raise MissingFunctionDefinition(functionName)

        return function

    def run(self):
        if self.studentSubmission == None:
            raise RuntimeError("INVALID STATE: Submission was NONE when should be a non-none type!")
        
        module = self.attemptToImport()
        
        self.applyMocks(module)

        if self.setupCode is not None:
            # apply to actual imported module
            exec(self.setupCode, vars(module))

            if self.AUTOGRADER_SETUP_NAME not in vars(module):
                raise InvalidTestCaseSetupCode()

            setUpCode = self.getMethod(module, self.AUTOGRADER_SETUP_NAME)

            setUpCode()

        functionToCall = self.getMethod(module, self.functionToCall)

        return functionToCall(*self.parameters)
