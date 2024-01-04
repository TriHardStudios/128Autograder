import unittest


@unittest.skip("AST Validators: not implemented")
class TestAstValidators(unittest.TestCase):
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
