import sys
from abc import ABC, abstractmethod
import importlib
from types import ModuleType

from StudentSubmission.common import MissingFunctionDefinition, InvalidTestCaseSetupCode


class Runner(ABC):
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
        self.studentSubmissionCode = None
        self.mocks: dict[str, object] | None = None
        self.setupCode = None

    def setSubmission(self, _code):
        self.studentSubmissionCode = _code

    def setMocks(self, _mocks: dict[str, object]):
        self.mocks = _mocks

    def getMocks(self) -> dict[str, dict[str, object]] | None:
        return self.mocks

    def setSetupCode(self, _setupCode):
        self.setupCode = compile(_setupCode, "setup_code", "exec")

    def applyMocks(self) -> None:
        """
        This function applies the mocks to the student's submission at the module level.

        :raises AttributeError: If a mock name cannot be resolved
        """
        if not self.mocks:
            return

        currentModule = sys.modules[__name__]

        for mockName, mock in self.mocks.items():
            setattr(currentModule, mockName, mock)

    @abstractmethod
    def run(self):
        raise NotImplementedError("Must use implementation of runner.")

    def __call__(self):
        return self.run()


class MainModuleRunner(Runner):
    def run(self):
        exec(self.studentSubmissionCode, {'__name__': "__main__"})


class FunctionRunner(Runner):

    def __init__(self, _functionToCall: str, *args):
        super().__init__()
        self.functionToCall: str = _functionToCall
        self.args = args

    @staticmethod
    def applyImports(_imports):
        currentModule = sys.modules[__name__]

        for moduleName in _imports:
            library = importlib.import_module(moduleName)
            setattr(currentModule, moduleName, library)

    def run(self):
        exec(self.studentSubmissionCode)
        importedModules = [localName for localName, localValue in locals().items() if
                           isinstance(localValue, ModuleType)]
        self.applyMocks()
        self.applyImports(importedModules)
        if self.functionToCall not in locals().keys():
            raise MissingFunctionDefinition(self.functionToCall)

        if self.setupCode is not None:
            exec(self.setupCode)

            if self.AUTOGRADER_SETUP_NAME not in locals().keys():
                raise InvalidTestCaseSetupCode()

            locals()[self.AUTOGRADER_SETUP_NAME]()

        functionToCall = locals()[self.functionToCall]

        return functionToCall(*self.args)
