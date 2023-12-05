from typing import Dict, Generic, List, Optional as OptionalType, TypeVar
from dataclasses import dataclass
import requests

from schema import And, Optional, Regex, Schema, SchemaError

from .common import BaseSchema, MissingParsingLibrary, InvalidConfigException


@dataclass(frozen=True)
class BuildConfiguration:
    use_starter_code: bool
    use_data_files: bool
    allow_private: bool

@dataclass(frozen=True)
class PythonConfiguration:
    extra_packages: List[Dict[str, str]]

@dataclass(frozen=True)
class BasicConfiguration:
    autograder_version: str
    enforce_submission_limit: bool
    submission_limit: int
    take_highest: bool
    allow_extra_credit: bool
    perfect_score: int
    max_score: int
    python: OptionalType[PythonConfiguration] = None

@dataclass(frozen=True)
class AutograderConfiguration:
    assignment_name: str
    semester: str
    config: BasicConfiguration
    build: BuildConfiguration


class AutograderConfigurationSchema(BaseSchema[AutograderConfiguration]):
    TAGS_ENDPOINT = "https://api.github.com/repos/CSCI128/128Autograder/tags"

    @staticmethod
    def getAvailableTags() -> List[str]:
        headers = {"X-GitHub-Api-Version": "2022-11-28"}

        tags = requests.get(url=AutograderConfigurationSchema.TAGS_ENDPOINT, headers=headers).json()

        return [el["name"] for el in tags]

    def __init__(self):
        self.TAGS = self.getAvailableTags()

        self.currentSchema: Schema = Schema(
            {
                "assignment_name": And(str, Regex(r"^(\w+-?)+$")),
                "semester": And(str, Regex(r"^(F|S|SUM)\d{2}$")),
                "config": {
                    "autograder_version": And(str, lambda x: x in self.TAGS),
                    "enforce_submission_limit": bool,
                    Optional("submission_limit", default=1000): And(int, lambda x: x >= 1),
                    Optional("take_highest", default=True): bool,
                    Optional("allow_extra_credit", default=False): bool,
                    "perfect_score": And(int, lambda x: x >= 1),
                    "max_score": And(int, lambda x: x >= 1),
                    Optional("python", default=None): {
                        Optional("extra_packages", default=lambda: []): [{
                            "name": str,
                            "version": str,
                        }],
                    },
                },
                "build": {
                    "use_starter_code": bool,
                    "use_data_files": bool,
                    Optional("allow_private", default=True): bool,

                }
            },
            ignore_extra_keys=False, name="ConfigSchema"
        )

    def validate(self, data: Dict) -> Dict:
        try:
            return self.currentSchema.validate(data)
        except SchemaError as schemaError:
            raise InvalidConfigException(str(schemaError))


    def build(self, data: Dict) -> AutograderConfiguration:
        if data["config"]["python"] is not None:
            data["config"]["python"] = PythonConfiguration(**data["config"]["python"])


        data["config"] = BasicConfiguration(**data["config"])
        data["build"] = BuildConfiguration(**data["build"])

        return AutograderConfiguration(**data)

T = TypeVar("T")
class AutograderConfigurationBuilder(Generic[T]):
    DEFAULT_CONFIG_FILE = "./config.toml"

    def __init__(self, configSchema: BaseSchema[T] = AutograderConfigurationSchema()):
        self.schema: BaseSchema[T] = configSchema
        self.data: Dict = {}


    def fromTOML(self, file=DEFAULT_CONFIG_FILE):
        try:
            from tomlkit import loads
        except ModuleNotFoundError:
            raise MissingParsingLibrary("tomlkit", "AutograderConfigurationBuilder.fromTOML")

        with open(file, 'r') as r:
            self.data = loads(r.read())

        return self

    # Really easy to add support for other file formats. 
    # YAML or JSON would work as well

    # For now, not allowing any configuration in code. Thankfully thats really easy to add in the future
    
    def build(self) -> T:
        self.data = self.schema.validate(self.data)
        return self.schema.build(self.data)






    

