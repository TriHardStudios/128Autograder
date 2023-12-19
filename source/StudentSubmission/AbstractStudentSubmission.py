import abc
from os import PathLike
from typing import Generic, List, Set, TypeVar, Any, Union

from .common import ValidationError

from .AbstractValidator import AbstractValidator
from .GenericValidators import SubmissionPathValidator

T = TypeVar("T")

# for some reason this has to be TBuilder??
TBuilder = TypeVar("TBuilder", bound="AbstractStudentSubmission[Any]")

class AbstractStudentSubmission(abc.ABC, Generic[T]):
    def __init__(self):
        self.submissionRoot: Union[PathLike, str] = "."
        # default valaidators
        self.validators: Set[AbstractValidator] = {
            SubmissionPathValidator()
        }
        self.validationErrors: List[Exception] = []


    def setSubmissionRoot(self: TBuilder, submissionRoot: str) -> TBuilder:
        self.submissionRoot = submissionRoot
        return self

    def addValidator(self: TBuilder, validator: AbstractValidator) -> TBuilder:
        self.validators.add(validator)
        return self
    
    @abc.abstractmethod
    def load(self: TBuilder) -> TBuilder:
        pass

    def validate(self: TBuilder) -> TBuilder:

        for validator in self.validators:
            validator.setup(self)
            validator.run()
            self.validationErrors.extend(validator.collectErrors())

        if self.validationErrors:
            raise ValidationError(self.validationErrors)

        return self

    @abc.abstractmethod
    def build(self: TBuilder) -> TBuilder:
        pass


    @abc.abstractmethod
    def getExecutableSubmission(self) -> T:
        pass

    def getSubmissionRoot(self) -> Union[PathLike, str]:
        return self.submissionRoot
    





