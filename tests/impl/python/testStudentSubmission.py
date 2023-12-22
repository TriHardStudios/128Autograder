import io
import os
import shutil
import string
import subprocess
import sys
import unittest
from unittest.mock import patch
from io import StringIO
import random
from StudentSubmission.common import ValidationError

from StudentSubmissionImpl.Python import PythonSubmission
from StudentSubmissionImpl.Python.common import FileTypeMap


class TestStudentSubmission(unittest.TestCase):
    TEST_FILE_DIRECTORY: str = "./testFiles"
    TEST_FILE_MAIN: str = "\n" \
                          "if __name__ == '__main__':" \
                          " print('TEST_FILE_MAIN')\n"

    TEST_FILE_NON_MAIN: str = "\n" \
                              "print('TEST_FILE_NON_MAIN')\n"

    def setUp(self) -> None:
        if os.path.exists(self.TEST_FILE_DIRECTORY):
            shutil.rmtree(self.TEST_FILE_DIRECTORY)
        os.mkdir(self.TEST_FILE_DIRECTORY)

    def tearDown(self) -> None:
        if os.path.exists(self.TEST_FILE_DIRECTORY):
            shutil.rmtree(self.TEST_FILE_DIRECTORY)

    def testDiscoverMainModuleSinglePy(self):
        filename = os.path.join(self.TEST_FILE_DIRECTORY, "non_main.py")

        with open(filename, 'w') as w:
            w.writelines(self.TEST_FILE_NON_MAIN)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                .allowLooseMainMatching()\
                .allowTestFiles()\
                .allowRequirements()\
                .load()\
                .build()\
                .validate()

        self.assertIn(filename, submission.getDiscoveredFileMap()[FileTypeMap.PYTHON_FILES])


    def testDiscoverFileWithDashes(self):
        filename = os.path.join(self.TEST_FILE_DIRECTORY, "file-with-dashes.py")

        with open(filename, 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                .allowLooseMainMatching()\
                .load()\
                .build()\
                .validate()

        self.assertIn(filename, submission.getDiscoveredFileMap()[FileTypeMap.PYTHON_FILES])

    def testDiscoverFileTest(self):
        filename = os.path.join(self.TEST_FILE_DIRECTORY, "test.py")

        with open(filename, 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                .allowTestFiles()\
                .load()\
                .build()\
                .validate()

        self.assertIn(filename, submission.getDiscoveredFileMap()[FileTypeMap.TEST_FILES])


    def testDiscoverMainModuleRandomNonPy(self):
        filename = os.path.join(self.TEST_FILE_DIRECTORY, "main.py")
        with open(filename, 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        for _ in range(10):
            fileName = "".join([random.choice(string.ascii_letters) for _ in range(10)])

            with open(os.path.join(self.TEST_FILE_DIRECTORY, fileName), 'w') as w:
                w.writelines("RAND")

        submission = PythonSubmission()\
                .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                .load()\
                .build()\
                .validate()

        self.assertIn(filename, submission.getDiscoveredFileMap()[FileTypeMap.PYTHON_FILES])
        self.assertEqual(1, len(submission.getDiscoveredFileMap()[FileTypeMap.PYTHON_FILES]))

    def testDiscoverNoPyFiles(self):
        for _ in range(10):
            fileName = "".join([random.choice(string.ascii_letters) for _ in range(10)])

            with open(os.path.join(self.TEST_FILE_DIRECTORY, fileName), 'w') as w:
                w.writelines("RAND")

        with self.assertRaises(ValidationError) as error:
            PythonSubmission()\
                    .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                    .allowLooseMainMatching()\
                    .load()\
                    .build()\
                    .validate()

        exceptionText = str(error.exception)

        self.assertIn("Expected at least one `.py` file", exceptionText)
        self.assertIn("Are you writing your code in a file that ends with `.py`", exceptionText)

    def testDiscoverNoMainPyFile(self):
        fileNames = []

        for _ in range(10):
            fileName = "".join([random.choice(string.ascii_letters) for _ in range(10)]) + ".py"

            fileNames.append(fileName)

            with open(os.path.join(self.TEST_FILE_DIRECTORY, fileName), 'w') as w:
                w.writelines("RAND")

        with self.assertRaises(ValidationError) as error:
            PythonSubmission()\
                    .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                    .allowLooseMainMatching()\
                    .load()\
                    .build()\
                    .validate()

        exceptionText = str(error.exception)

        self.assertIn(fileNames[3], exceptionText)
        self.assertIn("Expected one `.py` file", exceptionText)
        self.assertIn("delete extra `.py` files", exceptionText)


    def testDiscoverTestFiles(self):
        testFileNames: list[str] = [
            "test.py",
            "testFile.py",
            "test_file.py",
            "test_FileWith_longName.py"
        ]

        for file in testFileNames:
            with open(os.path.join(self.TEST_FILE_DIRECTORY, file), 'w') as w:
                w.writelines("pass")

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        submission = PythonSubmission()\
                    .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                    .allowTestFiles()\
                    .allowLooseMainMatching()\
                    .load()\
                    .build()\
                    .validate()

        testFileNames = [f"{os.path.join(self.TEST_FILE_DIRECTORY, file)}" for file in testFileNames]

        self.assertCountEqual(testFileNames, submission.getDiscoveredFileMap()[FileTypeMap.TEST_FILES])
        self.assertEqual(1, len(submission.getDiscoveredFileMap()[FileTypeMap.PYTHON_FILES]))

    @patch('sys.stdout', new_callable=StringIO)
    def testDiscoverMainModuleManyPy(self, capturedStdout):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "non_main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_NON_MAIN)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                .load()\
                .build()\
                .validate()

        exec(submission.getExecutableSubmission(), {'__name__': "__main__"})

        self.assertEqual("TEST_FILE_MAIN\n", capturedStdout.getvalue())

    def testAddPackage(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        submission = PythonSubmission()\
                .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                .addPackage("pip-install-test")\
                .load()\
                .build()\
                .validate()

    def testGetPackagesFromRequirements(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "requirements.txt"), 'w') as w:
            w.writelines("pip-install-test==0.5\n")

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines("import pip_install_test")

        submission = PythonSubmission()\
                .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                .allowRequirements()\
                .load()\
                .build()\
                .validate()

        self.assertEqual({"pip-install-test": "0.5"}, submission.getExtraPackages())


    def testNonExistentPackageInRequirements(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "requirements.txt"), 'w') as w:
            w.writelines("does-not-exist==0.5\n")

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines("import pip_install_test")

        submission = PythonSubmission()\
                .setSubmissionRoot(self.TEST_FILE_DIRECTORY)\
                .allowRequirements()\
                .load()\
                .build()\
                .validate()

    def testDisallowedFunctionPresent(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "non_main.py"), 'w') as w:
            w.writelines("\n"
                         "int(16, 4)\n"
                         )

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, ["int(_, 4)"])

        submission.validateSubmission()

        self.assertFalse(submission.isSubmissionValid())

        self.assertIn("Invalid Function Calls", submission.getValidationError())

    def testDisallowedFunctionInOtherModule(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "mod1.py"), 'w') as w:
            w.writelines("\n"
                         "int(16, 4)\n"
                         "int(4)"
                         )

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines("import mod1\n"
                         "int(16, 5)\n"
                         "int(8, 3)\n"
                         "int(1, 2)\n"
                         "int(8, 8)\n"
                         )

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, ["int(_,4)"])

        submission.validateSubmission()

        self.assertFalse(submission.isSubmissionValid())

        self.assertIn("Invalid Function Calls", submission.getValidationError())
        self.assertIn("int: called 1 times", submission.getValidationError())

    def testDisallowedFunctionNamePresent(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines("\n"
                         "eval('Hello', 16, 'wheeeee')\n"
                         "eval('different parameters!')\n"
                         )
        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, ["eval()"])

        submission.validateSubmission()

        self.assertFalse(submission.isSubmissionValid())

        self.assertIn("Invalid Function Calls", submission.getValidationError())
        self.assertIn("eval: called 2 times", submission.getValidationError())

    def testDisallowedFunctionNotPresent(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "non_main.py"), 'w') as w:
            w.writelines("\n"
                         "int(16, 5)\n"
                         "int(8, 3)\n"
                         "int(1, 2)\n"
                         "int(8, 8)\n"
                         "int(4)"
                         )

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, ["int(_, 4)"])

        submission.validateSubmission()

        self.assertTrue(submission.isSubmissionValid())

    @patch('sys.stdout', new_callable=StringIO)
    def testImportLibrary(self, capturedStdout):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "file.py"), 'w') as w:
            w.writelines("\n"
                         "import math\n"
                         "print(math.floor(3.999))\n"
                        )

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)
        submission.validateSubmission()

        self.assertTrue(submission.isSubmissionValid())
        self.assertEqual({}, submission.getImports())

        exec(submission.getStudentSubmissionCode())

        self.assertEqual("3\n", capturedStdout.getvalue())

    def testModules(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "mod1.py"), 'w') as w:
            w.writelines("\n"
                         "def fun1():\n"
                         "  print('fun1')\n"
                         )

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines("from mod1 import fun1\n"
                         "fun1()\n"
                         )

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)

        submission.validateSubmission()

        self.assertTrue(submission.isSubmissionValid())

        self.assertEqual({os.path.join(self.TEST_FILE_DIRECTORY, "mod1.py"): "mod1.py"}, submission.getImports())
