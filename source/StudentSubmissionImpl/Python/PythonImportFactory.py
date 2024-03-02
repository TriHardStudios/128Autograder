from typing import Type, Optional
from importlib.abc import MetaPathFinder


class PythonImportFactory:
    moduleFinder: Optional[MetaPathFinder] = None

    @classmethod
    def setModuleFinder(cls, moduleFinder: Type[MetaPathFinder]):
        cls.moduleFinder = moduleFinder()
    

    @classmethod
    def registerFile(cls, pathToFile: str, importName: str):
        if cls.moduleFinder == None:
            raise AttributeError("Invalid State: Module finder is none")
        if "addModule" in vars(cls.moduleFinder):
            raise AttributeError("Invalid ModuleFinder for registration")

        cls.moduleFinder.addModule(importName, pathToFile)
    
    @classmethod
    def buildImport(cls):
        return cls.moduleFinder
