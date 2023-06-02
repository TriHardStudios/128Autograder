import unittest.mock
from abc import ABC, abstractmethod


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

    def __init__(self):
        self.studentSubmissionCode = None
        self.mocks: dict[str, unittest.mock.Mock] | None = None

    def setSubmission(self, _code):
        self.studentSubmissionCode = _code

    def setMocks(self, _mocks: dict[str, unittest.mock.Mock]):
        self.mocks = _mocks

    def applyMocks(self) -> None:
        """
        This function applies the mocks in the student's submission by using reflection
        on the locals and globals. Overriding locals is preferred to globals.
        If the mock name cannot be resolved, then an attribute error is raised

        :raises AttributeError: If a mock name cannot be resolved in either the globals in locals
        """
        if not self.mocks:
            return

        for [mockName, mock] in self.mocks.items():
            # Might need to use setattr here for fully qualified names
            if mockName in locals().keys():
                locals()[mockName] = mock
                continue
            if mockName in globals().keys():
                globals()[mockName] = mock
                continue

            raise AttributeError(f"Failed to resolve mock '{mockName}' in locals or globals")

    @abstractmethod
    def run(self):
        raise NotImplementedError("Must use implementation of runner.")

    def __call__(self):
        return self.run()


class MainModuleRunner(Runner):
    def run(self):
        exec(self.studentSubmissionCode, {__name__: "__main__"}, {})


class FunctionRunner(Runner):
    def __init__(self, _functionToCall: str, *args):
        super().__init__()
        self.functionToCall: str = _functionToCall
        self.args = args

    def run(self):
        exec(self.studentSubmissionCode)
        self.applyMocks()
        return locals()[self.functionToCall](*self.args)
