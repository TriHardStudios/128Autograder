from typing import Dict, Set, override
import os
from Build.IBuild import DeployableEnvironments, FileMap, IBuild


class ExecutorBuild(IBuild):
    IGNORED_FILES = [__file__]

    @override
    def discover(self) -> Dict[DeployableEnvironments, Set[FileMap]]:
        moduleContents = os.listdir(os.path.abspath(__file__))

        discoveredFileMap: Set[FileMap] = {{'source': file, "dest": ''} for file in moduleContents if os.path.basename(file) not in ExecutorBuild.IGNORED_FILES}
        


        return {discoveredFileMap}
