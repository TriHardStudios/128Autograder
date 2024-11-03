import unittest
from unittest.mock import patch
import sys
import os
import shutil
from io import StringIO
import subprocess
import importlib.util
from utils.student import test_my_work as testMyWork
import random
import string

class TestStudentTestMyWork(unittest.TestCase):
    TEST_DIRECTORY: str = "./testData"
    SUBMISSION_DIRECTORY: str = os.path.join(TEST_DIRECTORY, "submission")

    
    def setUp(self) -> None:
        if os.path.exists(self.TEST_DIRECTORY):
            shutil.rmtree(self.TEST_DIRECTORY)

        os.mkdir(self.TEST_DIRECTORY)

        os.mkdir(self.SUBMISSION_DIRECTORY)


    def tearDown(self) -> None:
        if os.path.exists(self.TEST_DIRECTORY):
            shutil.rmtree(self.TEST_DIRECTORY)


    @patch('sys.stdout', new_callable=StringIO)
    def testStudentWorkNotPresent(self, capturedStdout: StringIO):
        result = testMyWork.verifyStudentWorkPresent(self.SUBMISSION_DIRECTORY)

        self.assertFalse(result)

        self.assertIn("No valid files found", capturedStdout.getvalue())
        
    
    @patch('sys.stdout', new_callable=StringIO)
    def testStudentWorkInvalidDirectory(self, capturedStdout: StringIO):
        result = testMyWork.verifyStudentWorkPresent("./DNE")

        self.assertFalse(result)

        self.assertIn("Failed to locate student work", capturedStdout.getvalue())


    @patch('sys.stdout', new_callable=StringIO)
    def testStudentWorkNoPy(self, capturedStdout: StringIO):
        for _ in range(10):
            fileName = "".join([random.choice(string.ascii_letters) for _ in range(10)])

            with open(os.path.join(self.SUBMISSION_DIRECTORY, fileName), 'w') as w:
                w.write("\n")

        result = testMyWork.verifyStudentWorkPresent(self.SUBMISSION_DIRECTORY)

        self.assertFalse(result)

        self.assertIn("No valid files found", capturedStdout.getvalue())

    def testStudentWorkPresentManyFiles(self):
        for _ in range(10):
            fileName = "".join([random.choice(string.ascii_letters) for _ in range(10)]) + ".py"

            with open(os.path.join(self.SUBMISSION_DIRECTORY, fileName), 'w') as w:
                w.write("\n")

        result = testMyWork.verifyStudentWorkPresent(self.SUBMISSION_DIRECTORY)

        self.assertTrue(result)

    @patch('sys.stdout', new_callable=StringIO)
    def testCleanPrevSubmission(self, _):
        for _ in range(10):
            fileName = "".join([random.choice(string.ascii_letters) for _ in range(10)]) + ".zip"

            with open(os.path.join(self.TEST_DIRECTORY, fileName), 'w') as w:
                w.write("\n")
        
        self.assertTrue(len(os.listdir(self.TEST_DIRECTORY)) > 1)
        
        testMyWork.cleanPreviousSubmissions(self.TEST_DIRECTORY)

        self.assertFalse(len(os.listdir(self.TEST_DIRECTORY)) > 1)

    def testChangesDetectedFirstRun(self):
        with open(os.path.join(self.SUBMISSION_DIRECTORY, "submission.py"), 'w') as w:
            w.write("First run!")

        result = testMyWork.verifyFileChanged(self.SUBMISSION_DIRECTORY)

        self.assertTrue(result)

    def testChangesDetectedManyRuns(self):
        with open(os.path.join(self.SUBMISSION_DIRECTORY, "submission.py"), 'w') as w:
            w.write("Frist run!")

        result = testMyWork.verifyFileChanged(self.SUBMISSION_DIRECTORY)

        self.assertTrue(result)

        with open(os.path.join(self.SUBMISSION_DIRECTORY, "submission.py"), 'a') as w:
            w.write("Second run!")

        result = testMyWork.verifyFileChanged(self.SUBMISSION_DIRECTORY)

        self.assertTrue(result)

    def testUnchangedDetected(self):
        with open(os.path.join(self.SUBMISSION_DIRECTORY, "submission.py"), 'w') as w:
            w.write("Frist run!")

        result = testMyWork.verifyFileChanged(self.SUBMISSION_DIRECTORY)

        self.assertTrue(result)

        result = testMyWork.verifyFileChanged(self.SUBMISSION_DIRECTORY)

        self.assertFalse(result)

    def testChangesInManyFiles(self):
        with open(os.path.join(self.SUBMISSION_DIRECTORY, "submission1.py"), 'w') as w:
            w.write("First run!")

        with open(os.path.join(self.SUBMISSION_DIRECTORY, "submission2.py"), 'w') as w:
            w.write("First run!")

        result = testMyWork.verifyFileChanged(self.SUBMISSION_DIRECTORY)
        
        self.assertTrue(result)

        with open(os.path.join(self.SUBMISSION_DIRECTORY, "submission2.py"), 'a') as w:
            w.write("Second run!")

        result = testMyWork.verifyFileChanged(self.SUBMISSION_DIRECTORY)
        
        self.assertTrue(result)

    def testEmptyJson(self):
        with open(os.path.join(self.SUBMISSION_DIRECTORY, testMyWork.FILE_HASHES_NAME), "w") as _:
            pass

        result = testMyWork.verifyFileChanged(self.SUBMISSION_DIRECTORY)

        self.assertTrue(result)

    @patch('sys.stdout', new_callable=StringIO)
    def testMissingPackage(self, _):
        self.assertIsNone(importlib.util.find_spec("pip_install_test"))

        res = testMyWork.verifyRequiredPackages({"pip_install_test": "pip-install-test"})

        self.assertIsNotNone(importlib.util.find_spec("pip_install_test"))

        self.assertTrue(res)

        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pip-install-test"], stdout=subprocess.DEVNULL)
        
    @patch('sys.stdout', new_callable=StringIO)
    def testPackageDoesNotExist(self, _):
        self.assertIsNone(importlib.util.find_spec("this_package_doesnt_exist"))

        res = testMyWork.verifyRequiredPackages({"this_package_doesnt_exist": "this_package_doesnt_exist"})

        self.assertFalse(res)

    @patch('sys.stdout', new_callable=StringIO)
    def testPackagesPresent(self, _):
        self.assertIsNotNone(importlib.util.find_spec("dill"))

        testMyWork.verifyRequiredPackages({"dill": "dill-install-test"})

        self.assertIsNotNone(importlib.util.find_spec("dill"))

    @patch('sys.stdout', new_callable=StringIO)
    def testMinPythonVersionTooLow(self, _):
        self.assertFalse(testMyWork.verifyPythonVersion((3, 12), (3, 11, 2, 'final', 0)))

    @patch('sys.stdout', new_callable=StringIO)
    def testMinPythonVersionValid(self, _):
        self.assertTrue(testMyWork.verifyPythonVersion((3, 11), (3, 11, 2, 'final', 0)))
        self.assertTrue(testMyWork.verifyPythonVersion((3, 11), (3, 12, 2, 'final', 0)))

    @patch('sys.stdout', new_callable=StringIO)
    def testWorkingDirectoryIncorrect(self, _):
        self.assertFalse(testMyWork.verifyWorkingDirectory("./sandbox"))
       
    @patch('sys.stdout', new_callable=StringIO)
    def testWorkingDirectoryIsCorrect(self, _):
        self.assertTrue(testMyWork.verifyWorkingDirectory(os.getcwd()))
