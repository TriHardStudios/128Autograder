import re

import unittest
import unittest.mock as mock

from utils.config.Config import AutograderConfigurationSchema, InvalidConfigException


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

def mockValidateImpl(_) -> bool: return True

class TestAutograderConfigurationSchema(unittest.TestCase):

    def setUp(self) -> None:
        self.configFile = {
            "assignment_name": "HelloWold",
            "semester": "F99",
            "config": {
                "impl_to_use": "Python",
                "autograder_version": "2.0.0",
                "test_directory": ".",
                "enforce_submission_limit": True,
                "perfect_score": 10,
                "max_score": 10,
                "python": {},
            },
            "build": {
                "use_starter_code": False,
                "use_data_files": False,
                "build_student": True,
                "build_gradescope": True,
            }
        }

    @staticmethod
    def createAutograderConfigurationSchema() -> AutograderConfigurationSchema:
        with mock.patch('requests.get', side_effect=mockRequestsGet):
            AutograderConfigurationSchema.validateImplSource = mockValidateImpl # type: ignore
            return AutograderConfigurationSchema()

    def testValidNoOptionalFields(self):
        schema = self.createAutograderConfigurationSchema()

        actual = schema.validate(self.configFile)
        self.assertIn("submission_limit", actual["config"])

    def testValidOptionalFields(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["config"]["python"] = {}
        actual = schema.validate(self.configFile)
        self.assertIn("extra_packages", actual["config"]["python"])

    def testInvalidOptionalFields(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["config"]["python"] = {}
        self.configFile["config"]["python"]["extra_packages"] = [{"name": "package"}]
        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)

    def testValidOptionalNestedFields(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["config"]["python"] = {}
        packages = [{"name": "package", "version": "1.0.0"}]
        self.configFile["config"]["python"]["extra_packages"] = packages

        actual = schema.validate(self.configFile)

        self.assertEqual(packages, actual["config"]["python"]["extra_packages"])

    def testExtraFields(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["new_field"] = "This field shouldn't exist"

        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)

    def testInvalidAutograderVersion(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["config"]["autograder_version"] = "0.0.0"

        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)


    def testBuildNoOptional(self):
        schema = self.createAutograderConfigurationSchema()

        data = schema.validate(self.configFile)

        actual = schema.build(data)

        self.assertEqual("F99", actual.semester)
        self.assertEqual(1000, actual.config.submission_limit)

    def testBuildWithOptional(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["config"]["python"] = {}

        data = schema.validate(self.configFile)

        actual = schema.build(data)

        self.assertIsNotNone(actual.config.python)
        self.assertIsNotNone(actual.config.python.extra_packages) # type: ignore

