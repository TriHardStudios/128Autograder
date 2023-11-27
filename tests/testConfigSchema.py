import re

import unittest
from unittest import mock
from utils.config import ConfigSchema, InvalidConfigException


def mockRequestsGet(url, **kwargs):
    class Response:
        def __init__(self, jsonData, status: int):
            self.jsonData = jsonData
            self.statusCode = status

        def json(self):
            return self.jsonData

    if re.match(r"https://api\.github\.com/repos/(\w|\d)+/(\w|\d)+/tags", url):
        data = \
            [
                {"name": "1.0.0"},
                {"name": "2.0.0"}
            ]

        return Response(data, 200)


class TestConfigSchema(unittest.TestCase):

    def setUp(self) -> None:
        with mock.patch('requests.get', side_effect=mockRequestsGet) as _:
            self.schema = ConfigSchema()

        self.configFile = {
            "assignment_name": "HelloWold",
            "semester": "F99",
            "config": {
                "autograder_version": "2.0.0",
                "enforce_submission_limit": True,
                "perfect_score": 10,
                "max_score": 10,
            },
            "build": {
                "use_starter_code": False,
                "use_data_files": False,
            }
        }

    def testValidNoOptionalFields(self):
        actual = self.schema.validate(self.configFile)
        self.assertIn("submission_limit", actual["config"])

    def testExtraFields(self):
        self.configFile["new_field"] = "This field shouldn't exist"

        with self.assertRaises(InvalidConfigException):
            self.schema.validate(self.configFile)

    def testInvalidAutograderVersion(self):
        self.configFile["config"]["autograder_version"] = "0.0.0"

        with self.assertRaises(InvalidConfigException):
            self.schema.validate(self.configFile)
