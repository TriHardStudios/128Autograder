from dataclasses import dataclass
import os
import shutil
import unittest

from utils.config import AutograderConfigurationBuilder
from utils.config.common import BaseSchema


@dataclass
class MockConfiguration:
    string_property: str
    int_property: int

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


