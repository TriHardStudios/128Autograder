import os.path
import sys
from unittest import TestSuite
from unittest import loader
from .baseTest import BaseTest


class TestRegister(TestSuite):
    def __init__(self):
        super().__init__()

        submissionDirectory: str = "/autograder/submission/"
        testPath: str = "/autograder/source/studentTests"
        if len(sys.argv) == 2 and sys.argv[1] == "--local":
            submissionDirectory = "../student/submission/"
            testPath = "studentTests"
        if len(sys.argv) == 3 and sys.argv[1] == "--unit-test-only":
            if not os.path.exists(sys.argv[2]):
                print(f"Fatal: {sys.argv[2]} does not exist")
                exit(2)
            if os.path.isfile(sys.argv[2]):
                sys.argv[2] = os.path.dirname(sys.argv[2]) + '/'
                print(f"Warning: Rewrote path as {sys.argv[2]}")

            testPath = "studentTests"
            submissionDirectory = sys.argv[2]

        BaseTest.submissionDirectory = submissionDirectory

        self.addTests(loader.defaultTestLoader.discover(testPath))



