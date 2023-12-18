import abc
from os import PathLike
from typing import Generic, List, TypeVar, Any, Union

from .AbstractValidator import AbstractValidator

G = TypeVar("G")
T = TypeVar("T")

TBuilder = TypeVar("TBuilder", bound="AbstractStudentSubmission[Any, Any]")


class StudentSubmissionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AbstractStudentSubmission(abc.ABCMeta, Generic[G, T]):
    def __init__(self):
        self.submissionRoot: Union[PathLike, str] = "."
        self.validators: List[AbstractValidator] = []


    def setSubmissionRoot(self: TBuilder, submissionRoot: str) -> TBuilder:
        self.submissionRoot = submissionRoot
        return self

    def addValidator(self: TBuilder, validator: AbstractValidator) -> TBuilder:
        self.validators.append(validator)
        return self
    
    @abc.abstractmethod
    def load(self: TBuilder) -> TBuilder:
        pass

    def validate(self: TBuilder) -> TBuilder:
        return self

    @abc.abstractmethod
    def build(self: TBuilder) -> TBuilder:
        pass


    @abc.abstractmethod
    def getExecutableSubmission(self) -> T:
        pass
    

    


