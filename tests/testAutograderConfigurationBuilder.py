from dataclasses import dataclass, field
import os
import shutil
import unittest

from utils.config.Config import AutograderConfigurationBuilder
from utils.config.common import BaseSchema


@dataclass
class MockConfiguration:
    string_property: str
    int_property: int
    config: dict = field(default_factory=dict)

class MockSchema(BaseSchema[MockConfiguration]):
    def __init__(self) -> None:
        pass

    def validate(self, data):
        return data

    def build(self, data) -> MockConfiguration:
        return MockConfiguration(**data)

class TestAutograderConfigurationBuilder(unittest.TestCase):
    DATA_DIRECTORY: str = "./testData/"
    DATA_FILE: str = os.path.join(DATA_DIRECTORY, "config.toml")

    def setUp(self) -> None:
        if os.path.exists(self.DATA_DIRECTORY):
            shutil.rmtree(self.DATA_DIRECTORY)

        os.mkdir(self.DATA_DIRECTORY)

    def tearDown(self) -> None:
        if os.path.exists(self.DATA_DIRECTORY):
            shutil.rmtree(self.DATA_DIRECTORY)

    def testBuildValidConfig(self):
        expectedString = "TOML!"
        expectedInt = 5

        with open(self.DATA_FILE, 'w') as w:
            w.write(
                f"string_property = '{expectedString}'\n"\
                f"int_property = {expectedInt}\n"
            )


        actual = \
            AutograderConfigurationBuilder(configSchema=MockSchema())\
            .fromTOML(file=self.DATA_FILE)\
            .build()

        self.assertEqual(expectedString, actual.string_property)
        self.assertEqual(expectedInt, actual.int_property)

    def testMalformedToml(self):
        expectedString = "TOML!"
        expectedInt = 5

        with open(self.DATA_FILE, 'w') as w:
            w.write(
                f"string_property: '{expectedString}'\n"\
                f"int_property = {expectedInt}\n"
            )


        with self.assertRaises(Exception):
            # Might want to wrap this in the future
            AutograderConfigurationBuilder(configSchema=MockSchema())\
                .fromTOML(file=self.DATA_FILE)\
                .build()

    def testCreateKeyAsNeeded(self):
        expectedDir = "./huzzah"

        with open(self.DATA_FILE, 'w') as w:
            w.write(
                f"string_property = 'hello'\n"\
                f"int_property = 0\n"
            )

        actual = \
                AutograderConfigurationBuilder(configSchema=MockSchema())\
                .fromTOML(file=self.DATA_FILE)\
                .setStudentSubmissionDirectory(expectedDir)\
                .build()

        self.assertEqual(expectedDir, actual.config["student_submission_directory"])


