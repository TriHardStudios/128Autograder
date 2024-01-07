import os
import shutil
import unittest
from unittest.mock import Mock

from utils.Build import Build, FilesEnum

class TestBuildFileDiscovery(unittest.TestCase):
    SANDBOX = "sandbox"
    TEST_ROOT = os.path.join(SANDBOX, "tests")
    DATA_SOURCE_ROOT = os.path.join(SANDBOX, "data")

    def setUp(self) -> None:
        if os.path.exists(self.SANDBOX):
            shutil.rmtree(self.SANDBOX)

        os.makedirs(self.TEST_ROOT, exist_ok=True)
        os.makedirs(self.DATA_SOURCE_ROOT, exist_ok=True)

        self.config = Mock()
        self.setUpConfig()

        self.privateFiles = ["test_private_1.py", "test_private_test2.py"]
        self.publicFiles = ["test.py", "test_public.py", "test_im_crying.py"]

    def setUpConfig(self):
        # There has to be a better way to setup this mock
        self.config.config.test_directory = self.TEST_ROOT
        self.config.build.allow_private=True
        self.config.build.private_tests_regex=r"^test_private_?\w*\.py$"
        self.config.build.public_tests_regex=r"^test_?\w*\.py$"
        self.config.build.use_stater_code=False
        self.config.build.starter_code_source = "."
        self.config.build.use_data_files = False
        self.config.build.data_files_source = self.DATA_SOURCE_ROOT


    def tearDown(self) -> None:
        if os.path.exists(self.SANDBOX):
            shutil.rmtree(self.SANDBOX)

    def writeTestFiles(self):
        for file in self.privateFiles:
            with open(os.path.join(self.TEST_ROOT, file), "w") as w:
                w.write("Private!")


        for file in self.publicFiles:
            with open(os.path.join(self.TEST_ROOT, file), "w") as w:
                w.write("Public!")


    def testDiscoverPublicAndPrivateTests(self):
        build = Build(self.config) # type: ignore

        self.writeTestFiles()

        result = build.discoverFiles()

        self.assertEqual(len(self.privateFiles), len(result[FilesEnum.PRIVATE_TEST]))
        self.assertEqual(len(self.publicFiles), len(result[FilesEnum.PUBLIC_TEST]))

    def testPrivateTestFilesWhenConflict(self):
        self.config.build.private_tests_regex=r"^test_?\w*\.py$"
        build = Build(self.config) # type: ignore

        self.writeTestFiles()

        result = build.discoverFiles()

        self.assertEqual(len(self.privateFiles) + len(self.publicFiles), len(result[FilesEnum.PRIVATE_TEST]))
        self.assertEqual(0, len(result[FilesEnum.PUBLIC_TEST]))

    def testAllPublicWhenPrivateFalse(self):
        self.config.build.allow_private = False

        build = Build(self.config) # type: ignore

        self.writeTestFiles()

        result = build.discoverFiles()

        self.assertEqual(0, len(result[FilesEnum.PRIVATE_TEST]))
        self.assertEqual(len(self.privateFiles) + len(self.publicFiles), len(result[FilesEnum.PUBLIC_TEST]))
