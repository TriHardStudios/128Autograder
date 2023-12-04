import re
from typing import Optional

import unittest
import unittest.mock as mock

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

    @staticmethod
    def createConfigSchema() -> ConfigSchema:
        with mock.patch('requests.get', side_effect=mockRequestsGet):
            return ConfigSchema()

    def testValidNoOptionalFields(self):
        schema = self.createConfigSchema()

        actual = schema.validate(self.configFile)
        self.assertIn("submission_limit", actual["config"])
        self.assertIn("python", actual["config"])
        self.assertNotIn("extra_packages", actual["config"]["python"])

    def testValidOptionalFields(self):
        schema = self.createConfigSchema()

        self.configFile["config"]["python"] = {}
        actual = schema.validate(self.configFile)
        self.assertIn("extra_packages", actual["config"]["python"])

    def testInvalidOptionalFields(self):
        schema = self.createConfigSchema()

        self.configFile["config"]["python"] = {}
        self.configFile["config"]["python"]["extra_packages"] = [{"name": "package"}]
        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)

    def testValidOptionalNestedFields(self):
        schema = self.createConfigSchema()

        self.configFile["config"]["python"] = {}
        packages = [{"name": "package", "version": "1.0.0"}]
        self.configFile["config"]["python"]["extra_packages"] = packages

        actual = schema.validate(self.configFile)

        self.assertEqual(packages, actual["config"]["python"]["extra_packages"])

    def testExtraFields(self):
        schema = self.createConfigSchema()

        self.configFile["new_field"] = "This field shouldn't exist"

        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)

    def testInvalidAutograderVersion(self):
        schema = self.createConfigSchema()

        self.configFile["config"]["autograder_version"] = "0.0.0"

        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)
