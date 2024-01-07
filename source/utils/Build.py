import os
import re
from typing import Dict, List 
from utils.config.Config import AutograderConfiguration
from enum import Enum

class FilesEnum(Enum):
    PUBLIC_TEST = 0
    PRIVATE_TEST = 1
    PUBLIC_DATA = 2
    PRIVATE_DATA = 3
    STARTER_CODE = 4

class Build():
    def __init__(self, config: AutograderConfiguration) -> None:
        self.config = config

    @staticmethod
    def _discoverTestFiles(allowPrivate: bool, 
                           privateTestFileRegex: re.Pattern, publicTestFileRegex: re.Pattern,
                           testDirectory: str,
                           discoveredPrivateFiles: List[str], discoveredPublicFiles: List[str]):
        """
        Description
        ---

        This function discovers the test files in the testDirectory and puts them in the correct list
        based on the regex matches.

        Note: If allowPrivate is false, then all files that match the private regex will be added to the public list

        :param allowPrivate: If private files should be treated as private
        :param privateTestFileRegex: The regex pattern used to match private test files
        :param publicTestFileRegex: The regex pattern used to match public test files
        :param discoveredPrivateFiles: The list that contains the private files to be copied
        :param discoveredPublicFiles: The list that contains the public files to be copied
        """

        # test discovery is non recursive for now
        test_files = [file for file in os.listdir(testDirectory) if os.path.isfile(os.path.join(testDirectory, file))]

        for file in test_files:
            path = os.path.join(testDirectory, file)
            # Dont need to worry about double checking, the private test will only be run once in both of these cases
            if allowPrivate and privateTestFileRegex.match(file):
                discoveredPrivateFiles.append(path)
            elif publicTestFileRegex.match(file) or privateTestFileRegex.match(file):
                discoveredPublicFiles.append(path)

    @staticmethod
    def _discoverDataFiles(allowPrivate: bool, dataFilesSource: str, 
                           discoveredPrivateFiles: List[str], discoveredPublicFiles: List[str]):
        """
        Description
        ---

        This function recursivly discovers the data files in the dataFilesSource.
        As opposed to the test file function, this will mark files as private if they contain 'private' anywhere in the path.

        Note: if allowPrivate is false, then all files that would otherwise be private will be added to the public list
        
        In the godforsaken event that some how we have a directory structure that exceeds 1000 folders, this will fail
        due to a recursion error

        :param allowPrivate: If private files should be treated as private
        :param dataFilesSource: The current search directory
        :param discoveredPrivateFiles: The list that contains the private files to be copied
        :param discoveredPublicFiles: the list that contains the public files to be copied
        """

        for file in os.listdir(dataFilesSource):
            # ignore hidden files + directories
            if file[0] == ".":
                continue

            path = os.path.join(dataFilesSource, file)

            # ignore any and all test files
            if "test" in path.lower():
                continue

            if os.path.isdir(path):
                Build._discoverDataFiles(allowPrivate, path, discoveredPrivateFiles, discoveredPublicFiles)
                continue

            if allowPrivate and "private" in path.lower():
                discoveredPrivateFiles.append(path)
                continue

            discoveredPublicFiles.append(path)

    def discoverFiles(self) -> Dict[FilesEnum, List[str]]:
        """
        Description
        ---

        This function discovers all of the user defined files to copy.
        See :ref:`_discoverTestFiles` and :ref:`_discoverDataFiles` for more information on how this process works

        :returns: A map containing all the user defined files to copy
        """
        config = self.config.build

        files: Dict[FilesEnum, List[str]] = {
            FilesEnum.PUBLIC_TEST: [],
            FilesEnum.PRIVATE_TEST: [],
            FilesEnum.PUBLIC_DATA: [],
            FilesEnum.PRIVATE_DATA: [],
            FilesEnum.STARTER_CODE: [],
        }

        self._discoverTestFiles(config.allow_private,
                                re.compile(config.private_tests_regex), re.compile(config.public_tests_regex),
                                self.config.config.test_directory, 
                                files[FilesEnum.PRIVATE_TEST], files[FilesEnum.PUBLIC_TEST])

        # imo, this is not worth moving into its function atm
        if config.use_starter_code:
            # we can assume that the file exists if the config has it
            files[FilesEnum.STARTER_CODE].append(config.stater_code_source)

        if config.use_data_files:
            self._discoverDataFiles(config.allow_private, config.data_files_source,
                                    files[FilesEnum.PRIVATE_DATA], files[FilesEnum.PUBLIC_DATA])

        return files

    def build(self):
        files = self.discoverFiles()
