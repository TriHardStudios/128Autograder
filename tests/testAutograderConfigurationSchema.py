import re

import unittest
import unittest.mock as mock

from utils.config.Config import AutograderConfigurationSchema, InvalidConfigException


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

        self.configFile["config"]["autograder_version"] = "0.0"

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

    def testBuildWithCImpl(self):
        schema = self.createAutograderConfigurationSchema()
        self.configFile["config"]["impl_to_use"] = "C"
        self.configFile["config"]["c"] = {}
        self.configFile["config"]["c"]["use_makefile"] = True
        self.configFile["config"]["c"]["clean_target"] = "clean"
        self.configFile["config"]["c"]["submission_name"] = "PROJECT"

        data = schema.validate(self.configFile)

        actual = schema.build(data)

        self.assertIsNotNone(actual.config.c)
        self.assertIsNotNone(actual.config.c.use_makefile) # type: ignore
        self.assertIsNotNone(actual.config.c.submission_name) # type: ignore

    def testBuildWithCImplInvalidName(self):
        schema = self.createAutograderConfigurationSchema()
        self.configFile["config"]["impl_to_use"] = "C"

        self.configFile["config"]["c"] = {}
        self.configFile["config"]["c"]["use_makefile"] = True
        self.configFile["config"]["c"]["clean_target"] = "clean"
        self.configFile["config"]["c"]["submission_name"] = ""

        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)

    def testMissingLocationStarterCode(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["build"]["use_starter_code"] = True

        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)

    def testMissingLocationDataFiles(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["build"]["use_data_files"] = True

        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)

    def testMissingImplConfig(self):
        schema = self.createAutograderConfigurationSchema()

        self.configFile["config"]["python"] = None

        with self.assertRaises(InvalidConfigException):
            schema.validate(self.configFile)
