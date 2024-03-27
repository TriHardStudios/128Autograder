from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Optional, List


class ModuleFinder(MetaPathFinder, Loader):
    def __init__(self, name: str, module: ModuleType) -> None:
        self.name: str = name
        self.module: bytes = dill.dumps(module, byref=True, recurse=True)
        self.modulesToReload: List[str] = [self.name]

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        return dill.loads(self.module)

    def exec_module(self, module):
        pass

    def find_spec(self, fullname, path, target=None) -> Optional[ModuleSpec]:
        if self.name != fullname:
            return None

        return ModuleSpec(self.name, self)

    def getModulesToReload(self) -> List[str]:
        return self.modulesToReload

