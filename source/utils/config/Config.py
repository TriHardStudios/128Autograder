from typing import Dict, Generic, List, Optional, TypeVar
from ConfigSchema import ConfigSchema

from utils.config.common import BaseSchema

G = TypeVar("G")

class ConfigBuilder(Generic[G]):
    DEFAULT_CONFIG_FILE = "./config.toml"

    def __init__(self, configSchema: BaseSchema[G] = ConfigSchema()):
        self.schema: BaseSchema[G] = configSchema
        self.data: Dict = {}


    def fromTOML(self, file=DEFAULT_CONFIG_FILE):
        try:
            from tomlkit import loads
        except ModuleNotFoundError:
            # Report error
            return self

        with open(file, 'r') as r:
            self.data = loads(r.read())

        return self

    # This actualy allows any 

    def build(self) -> G:
        self.data = self.schema.validate(self.data)
        return self.schema.build(self.data)



class Config:
    def __init__(self, ):
        pass








    

