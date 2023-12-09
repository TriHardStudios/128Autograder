import os
import unittest
from unittest import mock
import json

from utils import gradescopePostProcessing 
from utils.config import AutograderConfiguration


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


        self.autograderConfig.config.submission_limit = 1000
        self.autograderConfig.config.take_highest = True


        gradescopePostProcessing(self.autograderResults, self.autograderConfig, self.METADATA_PATH)

        self.assertEqual(0, self.autograderResults["score"])

    def testHigherPriorSubmission(self):
        self.metadata["previous_submissions"].append({
            "results": {
                "score": 1
            }

        })

        self.writeMetadata()

        self.autograderConfig.config.submission_limit = 1000
        self.autograderConfig.config.take_highest = True


        gradescopePostProcessing(self.autograderResults, self.autograderConfig, self.METADATA_PATH)

        self.assertEqual(1, self.autograderResults["score"])






