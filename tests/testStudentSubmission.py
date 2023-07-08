import io
import os
import shutil
import string
import sys
import unittest
from unittest.mock import patch
from io import StringIO
import random

from StudentSubmission import StudentSubmission


class TestStudentSubmission(unittest.TestCase):
    TEST_FILE_DIRECTORY: str = "./testFiles"
    TEST_FILE_MAIN: str = "\n" \
                          "print('TEST_FILE_MAIN')\n"

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
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "non_main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_NON_MAIN)

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)

        self.assertTrue(submission.isSubmissionValid())

    @patch('sys.stdout', new_callable=StringIO)
    def testDiscoverMainModuleManyPy(self, capturedStdout):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "non_main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_NON_MAIN)

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)

        self.assertTrue(submission.isSubmissionValid())

        exec(submission.getStudentSubmissionCode())

        self.assertEqual("TEST_FILE_MAIN\n", capturedStdout.getvalue())

    def testDiscoverMainModuleRandomNonPy(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_MAIN)

        for i in range(10):
            fileName = str([random.choice(string.ascii_letters) for i in range(10)])

            with open(os.path.join(self.TEST_FILE_DIRECTORY, fileName), 'w') as w:
                w.writelines("RAND")

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)

        self.assertTrue(submission.isSubmissionValid())

    def testDiscoverNoPyFiles(self):
        for i in range(10):
            fileName = str([random.choice(string.ascii_letters) for i in range(10)])

            with open(os.path.join(self.TEST_FILE_DIRECTORY, fileName), 'w') as w:
                w.writelines("RAND")

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)

        self.assertFalse(submission.isSubmissionValid())

        self.assertIn("No .py files were found", submission.getValidationError())

    def testDiscoverNoMainPyFile(self):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "non_main.py"), 'w') as w:
            w.writelines(self.TEST_FILE_NON_MAIN)

        for i in range(10):
            fileName = "".join([random.choice(string.ascii_letters) for i in range(10)]) + ".py"

            with open(os.path.join(self.TEST_FILE_DIRECTORY, fileName), 'w') as w:
                w.writelines("RAND")

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)

        self.assertFalse(submission.isSubmissionValid())

        self.assertIn("Unable to find main file", submission.getValidationError())

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

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)
        submission.validateSubmission()

        self.assertTrue(submission.isSubmissionValid())

        self.assertFalse(submission.getImports())

        testFileNames = [f"{os.path.join(self.TEST_FILE_DIRECTORY, file)}" for file in testFileNames]

        self.assertCountEqual(testFileNames, submission.getTestFiles())

    @patch('sys.stdout', new_callable=StringIO)
    def testDiscoverRequirementsFile(self, capturedStdout):
        with open(os.path.join(self.TEST_FILE_DIRECTORY, "requirements.txt"), 'w') as w:
            w.writelines("pip-install-test==0.5\n")

        with open(os.path.join(self.TEST_FILE_DIRECTORY, "main.py"), 'w') as w:
            w.writelines("import pip_install_test")

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)
        submission.validateSubmission()

        submission.installRequirements()

        self.assertTrue(submission.isSubmissionValid())
        exec(submission.getStudentSubmissionCode())

        self.assertIn("You installed a pip module.", capturedStdout.getvalue())

        submission.removeRequirements()

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
