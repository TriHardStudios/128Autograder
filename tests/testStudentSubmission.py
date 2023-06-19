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
        os.mkdir(self.TEST_FILE_DIRECTORY)

    def tearDown(self) -> None:
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
            fileName = str([random.choice(string.ascii_letters) for i in range(10)]) + ".py"

            with open(os.path.join(self.TEST_FILE_DIRECTORY, fileName), 'w') as w:
                w.writelines("RAND")

        submission: StudentSubmission = StudentSubmission(self.TEST_FILE_DIRECTORY, None)

        self.assertFalse(submission.isSubmissionValid())

        self.assertIn("Unable to find main file", submission.getValidationError())
