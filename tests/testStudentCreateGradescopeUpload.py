import os
import random
import shutil
import string
import unittest
from unittest.mock import MagicMock, patch
import zipfile

import create_gradescope_upload as createGradescopeUpload

class TestStudentCreateGradescopeUpload(unittest.TestCase):
    # These tests should prolly be expanded
    STUDENT_WORK_FOLDER = "student_work/"

    def setUp(self) -> None:
        self.workingDirectory = os.getcwd()
        os.mkdir(self.STUDENT_WORK_FOLDER)
        with open(os.path.join(self.STUDENT_WORK_FOLDER, "submission.py"), 'w') as w:
            w.write("")

        with open(os.path.join(self.STUDENT_WORK_FOLDER, ".keep"), 'w') as w:
            w.write("")


    def tearDown(self) -> None:
        if self.workingDirectory != os.getcwd():
            os.chdir(self.workingDirectory)

        shutil.rmtree(self.STUDENT_WORK_FOLDER)
        
        # clean up any zip files
        for file in os.listdir("."): 
            if os.path.isfile(file) and file[-4:] == ".zip":
                os.remove(file) 



    def testAddFolderToZipOnePy(self):
        zipMock = MagicMock(spec=zipfile.ZipFile)

        createGradescopeUpload.addFolderToZip(zipMock, self.STUDENT_WORK_FOLDER)

        writeMock: MagicMock = zipMock.write

        writeMock.assert_called_once()
        writeMock.assert_called_with(os.path.join(self.STUDENT_WORK_FOLDER, "submission.py"))


    def testAddFolderToZipDataFilesOnePy(self):
        for _ in range(10):
            randomName = "".join([random.choice(string.ascii_lowercase) for _ in range(10)]) + ".dat"

            with open(os.path.join(self.STUDENT_WORK_FOLDER, randomName), 'w') as w:
                w.write("")

        zipMock = MagicMock(spec=zipfile.ZipFile)

        createGradescopeUpload.addFolderToZip(zipMock, self.STUDENT_WORK_FOLDER)

        writeMock: MagicMock = zipMock.write

        writeMock.assert_called_once()
        writeMock.assert_called_with(os.path.join(self.STUDENT_WORK_FOLDER, "submission.py"))

    @patch("create_gradescope_upload.ZipFile")
    def testGenerateZipFileOnePy(self, zipMock):
        zipFileMock = MagicMock()
        zipMock.return_value.__enter__ = zipFileMock

        createGradescopeUpload.generateZipFile(self.STUDENT_WORK_FOLDER)

        writeMock: MagicMock = zipFileMock().write

        writeMock.assert_called_once()
        writeMock.assert_called_with("submission.py")


    @patch("create_gradescope_upload.ZipFile") 
    def testGenerateZipFileDataFilesOnePy(self, zipMock):
        for _ in range(10):
            randomName = "".join([random.choice(string.ascii_lowercase) for _ in range(10)]) + ".dat"

            with open(os.path.join(self.STUDENT_WORK_FOLDER, randomName), 'w') as w:
                w.write("")
        
        zipFileMock = MagicMock()
        zipMock.return_value.__enter__ = zipFileMock

        createGradescopeUpload.generateZipFile(self.STUDENT_WORK_FOLDER)

        writeMock: MagicMock = zipFileMock().write

        writeMock.assert_called_once()
        writeMock.assert_called_with("submission.py")
