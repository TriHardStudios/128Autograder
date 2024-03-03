import importlib
import os
import shutil
import sys
import unittest

from StudentSubmissionImpl.Python.PythonImportFactory import PythonImportFactory

class TestPythonImportFactory(unittest.TestCase):
    TEST_FILE_DIRECTORY: str = "./sandbox"
    
    def setUp(self) -> None:
        if os.path.exists(self.TEST_FILE_DIRECTORY):
            shutil.rmtree(self.TEST_FILE_DIRECTORY)
        os.mkdir(self.TEST_FILE_DIRECTORY)

    def tearDown(self) -> None:
        if os.path.exists(self.TEST_FILE_DIRECTORY):
            shutil.rmtree(self.TEST_FILE_DIRECTORY)

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
        PythonImportFactory.registerFile(os.path.join(self.TEST_FILE_DIRECTORY, filename), "calc")
        sys.meta_path.insert(0, PythonImportFactory.buildImport())
        
        importedModule = importlib.import_module("calc")
        self.assertEqual(importedModule.sqrt(4), 2)

    def testImportErrorRaised(self):
        filename = "bad.py"

        PythonImportFactory.registerFile(os.path.join(self.TEST_FILE_DIRECTORY, filename), "bad")
        sys.meta_path.insert(0, PythonImportFactory.buildImport())

        with self.assertRaises(ImportError):
            importlib.import_module("bad")

    @unittest.skip("Not implemented")
    def testImportSubmodule(self):
        filename = "calc.py"
        self.writeTestFile(filename)
        PythonImportFactory.registerFile(os.path.join(self.TEST_FILE_DIRECTORY, filename), "a.calc")
        sys.meta_path.insert(0, PythonImportFactory.buildImport())
        import a.calc as calc
        self.assertEqual(calc.sqrt(4), 2)
