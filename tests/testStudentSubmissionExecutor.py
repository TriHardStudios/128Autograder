import unittest.mock
import unittest

import StudentSubmission.StudentSubmissionExecutor as StudentSubmissionExecutor

StudentSubmissionExecutor.RunnableStudentSubmission.run = unittest.mock.MagicMock(return_value=None)


class TestStudentSubmissionExecutor(unittest.TestCase):
    pass
