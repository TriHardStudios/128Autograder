import subprocess
from typing import List
import unittest
import os
import shutil
from unittest.mock import MagicMock
from StudentSubmission.common import ValidationError
from StudentSubmissionImpl.C.CSubmission import CSubmission
from StudentSubmissionImpl.C.common import FileTypeMap


class CSubmissionTests(unittest.TestCase):
    SANDBOX_LOCATION: str = "./sandbox"
    MAKEFILE_LOCATION: str = os.path.join(SANDBOX_LOCATION, "makefile")
    EXEC_FILE_LOCATION: str = os.path.join(SANDBOX_LOCATION, "execuable_file")

    @classmethod
    def setUpClass(cls) -> None:
        cls.subprocess = subprocess.Popen.__enter__
        cls.mock = MagicMock()
        subprocess.Popen.__enter__ = MagicMock()
        subprocess.Popen.__enter__.return_value = cls.mock

    def setUp(self) -> None:
        if os.path.exists(self.SANDBOX_LOCATION):
            shutil.rmtree(self.SANDBOX_LOCATION)

        os.mkdir(self.SANDBOX_LOCATION)


    def tearDown(self) -> None:
        if os.path.exists(self.SANDBOX_LOCATION):
            shutil.rmtree(self.SANDBOX_LOCATION)

        self.mock.reset_mock()

    @classmethod
    def tearDownClass(cls) -> None:
        subprocess.Popen.__enter__ = cls.subprocess

    @classmethod
    def setUpSubprocess(cls, returnCodes: List[int], stdouts: List[bytes], stderrs: List[bytes]):
        cls.mock.communicate = MagicMock()
        cls.mock.communicate.side_effect = [(out, err) for out, err in zip(stdouts, stderrs)]
        cls.mock.poll = MagicMock()
        cls.mock.poll.side_effect = returnCodes

    def testMakeCommandExsits(self):
        self.setUpSubprocess([0], [b""], [b""])
        with open(self.MAKEFILE_LOCATION, "w") as w:
            w.write("\n")

        submission = CSubmission("test")\
            .setSubmissionRoot(self.SANDBOX_LOCATION)\
            .enableMakefile()\
            .load()

        self.assertIn(self.MAKEFILE_LOCATION, submission.getFileMap()[FileTypeMap.MAKEFILE])

    def testMakeCommandDoesntExist(self):
        notFound = b"not found!"

        self.setUpSubprocess([1], [b""], [notFound])

        with open(self.MAKEFILE_LOCATION, "w") as w:
            w.write("\n")

        with self.assertRaises(ValidationError) as ex:
            CSubmission("test")\
                .setSubmissionRoot(self.SANDBOX_LOCATION)\
                .enableMakefile()\
                .load()

        exText = str(ex.exception)

        self.assertIn("MakeUnavailable", exText)
        self.assertIn(notFound.decode(), exText)

    def testBuildPassAll(self):
        self.setUpSubprocess([0, 0, 0], [b"", b"", b""], [b"", b"", b""])

        with open(self.MAKEFILE_LOCATION, "w") as w:
            w.write("")

        with open(self.EXEC_FILE_LOCATION, "w") as w:
            w.write("")

        submission = CSubmission(os.path.basename(self.EXEC_FILE_LOCATION))\
            .setSubmissionRoot(self.SANDBOX_LOCATION)\
            .enableMakefile()\
            .setBuildTimeout(10)\
            .load()\
            .build()

        self.assertEqual(submission.getExecutableSubmission(), self.EXEC_FILE_LOCATION)

    def testBuildInBin(self):
        self.setUpSubprocess([0, 0, 0], [b"", b"", b""], [b"", b"", b""])

        with open(self.MAKEFILE_LOCATION, "w") as w:
            w.write("")

        binLoc = os.path.join(self.SANDBOX_LOCATION, "bin", os.path.basename(self.EXEC_FILE_LOCATION))
        otherDir = os.path.join(os.path.dirname(binLoc), "ignore", os.path.basename(self.EXEC_FILE_LOCATION))
        os.makedirs(os.path.dirname(binLoc), exist_ok=True)
        os.makedirs(os.path.dirname(otherDir), exist_ok=True)

        with open(binLoc, "w") as w:
            w.write("")

        with open(otherDir, "w") as w:
            w.write("")

        submission = CSubmission(os.path.basename(self.EXEC_FILE_LOCATION))\
            .setSubmissionRoot(self.SANDBOX_LOCATION)\
            .enableMakefile()\
            .load()\
            .build()

        self.assertEqual(submission.getExecutableSubmission(), binLoc)

    def testBuildCleanFail(self):
        self.setUpSubprocess([0, 1, 0], [b"", b"", b""], [b"", b"", b""])

        with open(self.MAKEFILE_LOCATION, "w") as w:
            w.write("")

        with open(self.EXEC_FILE_LOCATION, "w") as w:
            w.write("")

        submission = CSubmission(os.path.basename(self.EXEC_FILE_LOCATION))\
            .setSubmissionRoot(self.SANDBOX_LOCATION)\
            .enableMakefile()\
            .setCleanTargetName("clear")\
            .load()\
            .build()

        self.assertEqual(submission.getExecutableSubmission(), self.EXEC_FILE_LOCATION)

    def testBuildAllFail(self):
        buildErrorMessage = b"Build Fail!"
        self.setUpSubprocess([0, 1, 1], [b"", b"", b""], [b"", b"", buildErrorMessage])

        with open(self.MAKEFILE_LOCATION, "w") as w:
            w.write("")

        with open(self.EXEC_FILE_LOCATION, "w") as w:
            w.write("")

        with self.assertRaises(Exception) as ex:
            CSubmission(os.path.basename(self.EXEC_FILE_LOCATION))\
                .setSubmissionRoot(self.SANDBOX_LOCATION)\
                .enableMakefile()\
                .load()\
                .build()

        exText = str(ex.exception)

        self.assertIn(buildErrorMessage.decode(), exText)

    def testBuildNoMakefileExists(self):
        self.setUpSubprocess([0, 1, 0], [b"", b"", b""], [b"", b"", b""])

        # make sure at least one file exists so we actually trigger this error
        with open(self.EXEC_FILE_LOCATION, "w") as w:
            w.write("")

        with self.assertRaises(ValidationError) as ex:
            CSubmission(os.path.basename(self.EXEC_FILE_LOCATION))\
                .setSubmissionRoot(self.SANDBOX_LOCATION)\
                .enableMakefile()\
                .load()

        exText = str(ex.exception)

        self.assertIn("No makefiles found", exText)


    def testBuildNoExecutableCreated(self):
        self.setUpSubprocess([0, 1, 0], [b"", b"", b""], [b"", b"", b""])

        with open(self.MAKEFILE_LOCATION, "w") as w:
            w.write("")

        
        with self.assertRaises(ValidationError) as ex:
            CSubmission(os.path.basename(self.EXEC_FILE_LOCATION))\
                .setSubmissionRoot(self.SANDBOX_LOCATION)\
                .enableMakefile()\
                .load()\
                .build()


        exText = str(ex.exception)

        self.assertIn("No executable found with name", exText)



