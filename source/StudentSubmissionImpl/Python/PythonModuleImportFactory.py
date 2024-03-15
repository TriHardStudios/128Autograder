from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_loader
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Optional


class ModuleFinder(MetaPathFinder):
    def __init__(self, name, module: ModuleType) -> None:
        self.name = name
        self.module = module

    def find_spec(self, fullname, path, target=None):
        if self.name != fullname:
            return None

        return spec_from_loader(self.name, )

class ModuleLoader(Loader):
    def __init__(self, module: ModuleType) -> None:
        self.module: ModuleType = module

    def create_module(self, spec: ModuleSpec) -> Optional[ModuleType]:
        return self.module

