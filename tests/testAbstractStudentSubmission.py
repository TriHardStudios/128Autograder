import unittest
import os
import shutil

from StudentSubmission import AbstractStudentSubmission, AbstractValidator
from StudentSubmission.common import ValidationError, ValidationHook


class StudentSubmission(AbstractStudentSubmission[str]):
    def __init__(self):
        super().__init__()
        self.studentCode: str = "No code"

    def doLoad(self):
        self.studentCode = "Loaded code!"

    def doBuild(self):
        self.studentCode = "Built code!"

    def getExecutableSubmission(self) -> str:
        return self.studentCode


class CodeLoadedValidator(AbstractValidator):
    @staticmethod
    def getValidationHook() -> ValidationHook:
        return ValidationHook.POST_LOAD

    def __init__(self):
        super().__init__()
        self.code = ""

    def setup(self, studentSubmission):
        self.code = studentSubmission.studentCode

    def run(self):
        if not self.code:
            self.errors.append(Exception("Code was not loaded!"))


class FileExistsValidator(AbstractValidator):
    @staticmethod
    def getValidationHook() -> ValidationHook:
        return ValidationHook.PRE_LOAD

    def __init__(self, fileName):
        super().__init__()
        self.submissionRoot = ""
        self.fileName = fileName

    def setup(self, studentSubmission):
        self.submissionRoot = studentSubmission.getSubmissionRoot()

    def run(self):
        if self.fileName not in self.submissionRoot:
            self.errors.append(Exception(f"{self.fileName} does not exist!"))




class TestAbstractStudentSubmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.initalDirectory = os.getcwd() 
        cls.TEST_DIR = os.path.join(cls.initalDirectory, "sandbox")

    def setUp(self) -> None:
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)

        os.mkdir(self.TEST_DIR)
        os.chdir(self.TEST_DIR)

    def tearDown(self) -> None:
        os.chdir(self.initalDirectory)

        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)

    def testSetSubmissionRootExists(self):
        submissionRoot = "./submission"
        os.mkdir(submissionRoot)

        studentSubmission = StudentSubmission()\
                .setSubmissionRoot(submissionRoot)\
                .addValidator(CodeLoadedValidator())\
                .load()\
                .build()\
                .validate()

        self.assertEqual("Built code!", studentSubmission.getExecutableSubmission())

    def testSetSubmissionRootDoesntExist(self):
        submissionRoot = "./submission"
        with self.assertRaises(ValidationError) as validationError:
            StudentSubmission()\
                .setSubmissionRoot(submissionRoot)\
                .load()

        exceptionText = str(validationError.exception)

        self.assertIn("Validation Errors:", exceptionText)
        self.assertIn(f"1. {submissionRoot} does not exist", exceptionText)


    def testAddValidatorForExistingFile(self):
        filename = "file.txt"
        
        with self.assertRaises(ValidationError) as validationError:
            StudentSubmission()\
                .addValidator(FileExistsValidator(filename))\
                .setSubmissionRoot("./dne")\
                .load()

        exceptionText = str(validationError.exception)

        self.assertIn("2.", exceptionText)
        self.assertIn(f"{filename} does not exist", exceptionText)



    

    


