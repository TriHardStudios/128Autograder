import abc
import enum
from typing import Dict, Set, TypedDict

class DeployableEnvironments(enum.Enum):
    GRADESCOPE=1
    PRARIELEARN=2
    STUDENT=3


class FileMap(TypedDict):
    source_path: str
    dest_path: str


class IBuild(abc.ABC):
    @abc.abstractmethod
    def discover(self) -> Dict[DeployableEnvironments, Set[FileMap]]:
        raise NotImplemented()
