import enum
from types import CodeType
from typing import TypeVar, Tuple, Any, List, Final, Optional, Dict, overload, Union

from StudentSubmission.IRunner import IRunner, T
from StudentSubmission.common import InvalidRunner
from TestingFramework.SingleFunctionMock import SingleFunctionMock

Builder = TypeVar('Builder', bound="PythonRunnerBuilder")


class Parameter:
    def __init__(self, value: Optional[object] = None, autowiredName: Optional[str] = None):
        if value is not None and autowiredName is not None:
            raise InvalidRunner("Value and Autowire cannot both be defined.")

        if value is None and autowiredName is None:
            raise InvalidRunner("Exactly one of value and autowire must be defined.")

        self._useAutowire: Final[bool] = autowiredName is not None

        self._autowire: Final[str] = autowiredName

        self._value: Final[object] = value

    @property
    def useAutowire(self) -> bool:
        return self._useAutowire

    @property
    def autowire(self) -> str:
        if not self._useAutowire:
            raise AttributeError("Attempt to access autowire when autowire is null!")
        return self._autowire

    @property
    def value(self) -> object:
        if self._useAutowire:
            raise AttributeError("Attempt to access value when value is null!")
        return self._value


class PythonRunner(IRunner):

    def run(self) -> T:
        pass

class PythonRunnerBuilder:
    INJECTED_PREFIX: Final[str] = "INJECTED_"

    def __init__(self: Builder, submission: CodeType):
        self.submission: Final[CodeType] = submission
        self.parameters: List[Parameter] = []
        self.mocks: Dict[str, Optional[SingleFunctionMock]] = {}
        self.injectedMethods: Dict[str, CodeType] = {}
        self.useModuleEntrypoint: bool = False
        self.functionEntrypoint: Optional[str] = None

    def addParameter(self: Builder, parameter: Parameter) -> Builder:
        self.parameters.append(parameter)

        return self

    def addMock(self: Builder, name: str, mock: Optional[SingleFunctionMock]) -> Builder:
        if name in self.mocks:
            raise InvalidRunner(f"Mock '{name}' has already been added to the runner.")

        self.mocks[name] = mock

        return self

    def addInjectedCode(self: Builder, name: str, src: Optional[str] = None,
                        code: Optional[CodeType] = None) -> Builder:
        if name[0: len(PythonRunnerBuilder.INJECTED_PREFIX)] != PythonRunnerBuilder.INJECTED_PREFIX:
            raise InvalidRunner(
                f"Injected methods must be prefixed with '{PythonRunnerBuilder.INJECTED_PREFIX}'. Was '{name}'.")

        if src is not None and code is not None:
            raise InvalidRunner(f"Multiple injected method implementations provided. Expected either source *or* code.")

        if src is None and code is None:
            raise InvalidRunner(f"No injected method implementation provided. Expected *exactly* one.")

        if src is not None:
            try:
                code = compile(src, name, "exec")
            except SyntaxError as syntaxError:
                raise InvalidRunner(
                    f"Syntax Error when compiling injected method!\nEnsure that you are using dill.getsource(..., lstrip=True,...)\n{syntaxError}")
            except ValueError:
                raise InvalidRunner(f"Null Bytes detected when compiling injected method!")

        self.injectedMethods[name] = code

        return self

    def setEntrypoint(self: Builder, module: bool = False, function: Optional[str] = None) -> Builder:
        if module and function is not None:
            raise InvalidRunner(f"Duplicate entrypoints defined. Only one can be defined!")


        self.useModuleEntrypoint = module
        self.functionEntrypoint = function

        return self

    def build(self) -> PythonRunner:
        if self.functionEntrypoint and (PythonRunnerBuilder.INJECTED_PREFIX in self.functionEntrypoint and self.functionEntrypoint not in self.injectedMethods):
            raise InvalidRunner(f"Injected method '{self.functionEntrypoint}' has not been injected!")

        return PythonRunner()

