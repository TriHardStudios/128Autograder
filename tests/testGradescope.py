import os
import unittest
from unittest import mock
import json

from utils.Gradescope import gradescopePostProcessing 

class TestGradescopeUtils(unittest.TestCase):
    METADATA_PATH = "./metadata.json"

    def setUp(self) -> None:
        self.metadata = {
            "previous_submissions": []
        }

        self.autograderResults = {
            "score": 0
        }
        self.autograderConfig = mock.Mock()

    def tearDown(self) -> None:
        if os.path.exists(self.METADATA_PATH):
            os.remove(self.METADATA_PATH)

    def writeMetadata(self):
        with open(self.METADATA_PATH, 'w') as w:
            json.dump(self.metadata, w)

    def testNoPriorSubmissions(self):
        self.writeMetadata()

        self.autograderResults["score"] = 10

        self.autograderConfig.config.submission_limit = 3
        self.autograderConfig.config.take_highest = True

        gradescopePostProcessing(self.autograderResults, self.autograderConfig, self.METADATA_PATH)

        self.assertEqual(10, self.autograderResults["score"])

    def testHigherPriorSubmission(self):
        self.metadata["previous_submissions"].append({
            "results": {
                "score": 10
            }

        })

        self.writeMetadata()

        self.autograderConfig.config.submission_limit = 1000
        self.autograderConfig.config.take_highest = True


        gradescopePostProcessing(self.autograderResults, self.autograderConfig, self.METADATA_PATH)

        self.assertEqual(10, self.autograderResults["score"])

    def testLowerPreviousLimitExeceded(self):
        self.metadata["previous_submissions"].append({
            "results": {
                "score": 9
            }
        })

        self.metadata["previous_submissions"].append({
            "results": {
                "score": 9.5
            }
        })

        self.metadata["previous_submissions"].append({
            "results": {
                "score": 2
            }
        })

        self.autograderResults["score"] = 10

        self.writeMetadata()

        self.autograderConfig.config.submission_limit = 3
        self.autograderConfig.config.take_highest = True


        gradescopePostProcessing(self.autograderResults, self.autograderConfig, self.METADATA_PATH)

        self.assertEqual(9.5, self.autograderResults["score"])

    def testLowerPrevious(self):
        self.metadata["previous_submissions"].append({
            "results": {
                "score": 9
            }
        })

        self.metadata["previous_submissions"].append({
            "results": {
                "score": 9.5
            }
        })

        self.autograderResults["score"] = 10

        self.writeMetadata()

        self.autograderConfig.config.submission_limit = 3
        self.autograderConfig.config.take_highest = True


        gradescopePostProcessing(self.autograderResults, self.autograderConfig, self.METADATA_PATH)

        self.assertEqual(10, self.autograderResults["score"])

    def testInvalidPreviousSubmission(self):
        # This is a fix for the broken behavoir that we see if GS crashes

        self.metadata["previous_submissions"].append({
            "results": {}
        })

        self.metadata["previous_submissions"].append({
            "results": {}
        })

        self.autograderResults["score"] = 10

        self.writeMetadata()

        self.autograderConfig.config.submission_limit = 3
        self.autograderConfig.config.take_highest = True


        gradescopePostProcessing(self.autograderResults, self.autograderConfig, self.METADATA_PATH)

        self.assertEqual(10, self.autograderResults["score"])


