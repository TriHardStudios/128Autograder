import unittest
from unittest.mock import MagicMock
import subprocess
import os
import shutil
class CSubmissionProcessTests(unittest.TestCase):
    SANDBOX_LOCATION: str = "./test_files"
    EXEC_FILE_LOCATION: str = os.path.join(SANDBOX_LOCATION, "execuable_file")

    @classmethod
    def setUpClass(cls) -> None:
        cls.subprocess = subprocess.Popen
        cls.mock = MagicMock()
        subprocess.Popen = MagicMock(spec=subprocess.Popen)
        subprocess.Popen.communicate = cls.mock

    def setUp(self) -> None:
        if os.path.exists(self.SANDBOX_LOCATION):
            shutil.rmtree(self.SANDBOX_LOCATION)

        self.mock.reset_mock()

        os.mkdir(self.SANDBOX_LOCATION)


    def tearDown(self) -> None:
        if os.path.exists(self.SANDBOX_LOCATION):
            shutil.rmtree(self.SANDBOX_LOCATION)

        self.mock.reset_mock()

    @classmethod
    def tearDownClass(cls) -> None:
        subprocess.Popen = cls.subprocess

    @classmethod
    def setUpSubprocess(cls, returnCodes: List[int], stdouts: List[bytes], stderrs: List[bytes]):
        cls.mock.communicate = MagicMock()
        cls.mock.communicate.side_effect = [(out, err) for out, err in zip(stdouts, stderrs)]
        cls.mock.poll = MagicMock()
        cls.mock.poll.side_effect = returnCodes

