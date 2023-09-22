import unittest
from unittest.mock import patch
import os
import shutil
from io import StringIO
import test_my_work as testMyWork
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

    def testCleanPrevSubmission(self):
        for _ in range(10):
            fileName = "".join([random.choice(string.ascii_letters) for _ in range(10)]) + ".zip"

            with open(os.path.join(self.TEST_DIRECTORY, fileName), 'w') as w:
                w.write("\n")
        
        self.assertTrue(len(os.listdir(self.TEST_DIRECTORY)) > 1)
        
        testMyWork.cleanPreviousSubmissions(self.TEST_DIRECTORY)

        self.assertFalse(len(os.listdir(self.TEST_DIRECTORY)) > 1)



    

    


