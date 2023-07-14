import os.path
import sys
from unittest import TestSuite
from unittest import loader
from .BaseTest import BaseTest


class TestRegister(TestSuite):
    """
    This class is the base TestSuite for all tests written. It handles the discovery of the tests based on that the script is run in.
    """
    def __init__(self):
        super().__init__()

        submissionDirectory: str = "/autograder/submission/"
        testPath: str = "/autograder/source/studentTests"
        # If we are running locally - use a relative path
        if len(sys.argv) == 2 and sys.argv[1] == "--local":
            submissionDirectory = "../student/submission/"
            testPath = "studentTests"

        # Make sure we have the correct number of arguments to run in unit-test-only mode
        if len(sys.argv) == 2 and sys.argv[1] == "--unit-test-only":
            print(f"Fatal: Missing student submission directory")
            exit(2)

        # verify that we are able to access the submission directory
        if len(sys.argv) == 3 and sys.argv[1] == "--unit-test-only":
            if not os.path.exists(sys.argv[2]):
                print(f"Fatal: {sys.argv[2]} does not exist")
                exit(2)

            # TODO this does nothing bc it will never be true
            if os.path.isfile(sys.argv[2]):
                sys.argv[2] = os.path.dirname(sys.argv[2]) + '/'
                print(f"Warning: Rewrote path as {sys.argv[2]}")

            testPath = "studentTests"
            submissionDirectory = sys.argv[2]

        BaseTest.submissionDirectory = submissionDirectory

        self.addTests(loader.defaultTestLoader.discover(testPath))



