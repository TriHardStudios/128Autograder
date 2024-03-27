import importlib
import os
import shutil
import sys
from types import ModuleType
import unittest
import copy
import dill

from StudentSubmissionImpl.Python.PythonFileImportFactory import PythonFileImportFactory
from StudentSubmissionImpl.Python.PythonModuleMockImportFactory import ModuleFinder

class TestPythonImportFactory(unittest.TestCase):
    TEST_FILE_DIRECTORY: str = "./sandbox"
    
    def setUp(self) -> None:
        if os.path.exists(self.TEST_FILE_DIRECTORY):
            shutil.rmtree(self.TEST_FILE_DIRECTORY)
        os.mkdir(self.TEST_FILE_DIRECTORY)

        self.savedMetaPath = copy.deepcopy(sys.meta_path)

    def tearDown(self) -> None:
        if os.path.exists(self.TEST_FILE_DIRECTORY):
            shutil.rmtree(self.TEST_FILE_DIRECTORY)

        sys.meta_path = self.savedMetaPath

    def writeTestFile(self, filename):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, filename), 'w') as w:
            w.write(
                "import math\n"\
                "def sqrt(a):\n"\
                "   return math.sqrt(a)"
            )
        
    def testImportsFile(self):
        filename = "calc.py"
        self.writeTestFile(filename)
        PythonFileImportFactory.registerFile(os.path.join(self.TEST_FILE_DIRECTORY, filename), "calc")
        sys.meta_path.insert(0, PythonFileImportFactory.buildImport())
        
        importedModule = importlib.import_module("calc")
        self.assertEqual(importedModule.sqrt(4), 2)

    def testImportErrorRaised(self):
        filename = "bad.py"

        PythonFileImportFactory.registerFile(os.path.join(self.TEST_FILE_DIRECTORY, filename), "bad")
        sys.meta_path.insert(0, PythonFileImportFactory.buildImport())

        with self.assertRaises(ImportError):
            importlib.import_module("bad")

    def testImportedModuleIsSame(self):
        mod = ModuleType("random")
        expected = "autograder!"
        # for some reason macos and windows cache all of the system modules by default. WTF. This is dumb
        del sys.modules['random']

        setattr(mod, "name", expected)

        sys.meta_path.insert(0, ModuleFinder("random", mod))

        import random

        result = getattr(random, "name", None)

        self.assertEqual(result, expected)

    def testSerializeModule(self):
        mod = importlib.import_module("random")

        expected = lambda *_: "autograder!"

        setattr(mod, "randint", expected)

        serialized = dill.dumps(mod)

        actualMod = dill.loads(serialized)

        self.assertEqual(mod, actualMod)

        self.assertEqual(actualMod.randint(), expected())


