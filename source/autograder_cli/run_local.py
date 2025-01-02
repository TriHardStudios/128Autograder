import hashlib
import json
import os
import re
from typing import Dict, List, Optional

import BetterPyUnitFormat
import tomli

from autograder_platform.cli import AutograderCLITool
from autograder_platform.config.Config import AutograderConfigurationBuilder, AutograderConfiguration, \
    AutograderConfigurationProvider


class LocalAutograderCLI(AutograderCLITool):
    SUBMISSION_REGEX: re.Pattern = re.compile(r"^(\w|\s)+\.py$")
    FILE_HASHES_NAME = ".filehashes"

    def __init__(self):
        super().__init__("Local")

        self.config_location = ""

    def clean_previous_submissions(self, directory: str):
        """
        This function cleans out previous submissions if they exist.
        :param directory: the directory to run the detection in.
        """
        zip_files = [os.path.join(directory, file) for file in os.listdir(directory) if file[-4:] == ".zip"]
        if len(zip_files) > 0:
            self.print_info_message("Previous submissions found. Cleaning out old submission files")
            for file in zip_files:
                os.remove(file)

    def generate_hashes(self, submission_directory: str):
        """
        This function generates hashes for the files in submission directory.

        :param submission_directory: The directory to base all the hashes out of
        """

        pythonFiles = [
            os.path.join(submission_directory, file)
            for file in os.listdir(submission_directory)
            if self.SUBMISSION_REGEX.match(file)
        ]

        fileHashes: dict[str, str] = {}

        for file in pythonFiles:
            with open(file, 'rb') as r:
                # technically, this can lead to overflow issues if the file is too large.
                #  That shouldn't happen in this class hopefully
                fileBytes = r.read()
                fileHashes[file] = hashlib.md5(fileBytes, usedforsecurity=False).hexdigest()

        return fileHashes

    def verify_file_changed(self, submission_directory: str):
        """
        This function checks to see if a file has changed since the last run of this script.

        It stores its results in `submissionDirectory/.filehashes`. Currently it does not support sub directories.

        :param submission_directory: the directory that the student is doing their work in.

        :return: true if at least of the files changed.

        """

        FILE_HASHES_PATH = os.path.join(submission_directory, self.FILE_HASHES_NAME)

        if not os.path.exists(FILE_HASHES_PATH):
            with open(FILE_HASHES_PATH, 'w') as w:
                json.dump({}, w)

        with open(FILE_HASHES_PATH, 'r') as r:
            try:
                existingHashes = json.load(r)
            except json.JSONDecodeError:
                existingHashes = None

        newHashes = self.generate_hashes(submission_directory)

        with open(FILE_HASHES_PATH, 'w') as w:
            json.dump(newHashes, w)

        return existingHashes != newHashes

    @staticmethod
    def verify_working_directory(expected_path: str):
        pass

    def verify_student_work_present(self, submission_directory: str) -> bool:
        if not os.path.exists(submission_directory):
            self.print_error_message(self.SUBMISSION_ERROR, f"Failed to locate student work in {submission_directory}")
            return False

        # this doesn't catch files in folders. Something to be aware of for students
        files = [file for file in os.listdir(submission_directory) if self.SUBMISSION_REGEX.match(file)]

        if len(files) < 1:
            self.print_error_message(self.SUBMISSION_ERROR, f"No valid files found in submission directory.")
            self.print_error_message(self.SUBMISSION_ERROR, f"Found {os.listdir(submission_directory)}.")
            return False

        return True

    # @staticmethod
    # def verify_required_packages(package_to_verify: Dict[str, str]):
    #
    #     pass

    @staticmethod
    def discover_autograders(current_root: str, autograders: List[str]):
        contents = os.listdir(current_root)

        for path in contents:
            path = os.path.join(current_root, path)

            if "__" in path:
                continue

            if os.path.basename(path)[0] == ".":
                continue

            if os.path.isfile(path) and os.path.basename(path) == "config.toml":
                autograders.append(path)
                break

            if os.path.isdir(path):
                LocalAutograderCLI.discover_autograders(path, autograders)

    @staticmethod
    def get_autograder_name(path) -> Optional[str]:
        with open(path, 'rb') as rb:
            data = tomli.load(rb)

        if "assignment_name" not in data or not data["assignment_name"]:
            return None

        return data["assignment_name"]

    def select_root(self) -> Optional[str]:
        autograders = []

        full_path = os.path.abspath(".")

        self.print_info_message(f"Discovering autograders in {full_path}...")

        self.discover_autograders(full_path, autograders)

        if len(autograders) == 0:
            self.print_error_message(self.ENVIRONMENT_ERROR, f"Failed to locate any autograders in '{full_path}'!")
            self.print_error_message(self.ENVIRONMENT_ERROR,
                                     "Make sure that this script is being run in the same directory as your autograder!")
            return None

        if len(autograders) == 1:
            self.print_info_message(f"Selecting autograder config located at '{autograders[0]}'")
            return autograders[0]

        self.print_info_message(f"Multiple autograders found at {full_path}!")
        self.print_info_message(f"Please select the autograder you want to run")

        for i, path in enumerate(autograders):
            name = self.get_autograder_name(path)

            if name is None:
                continue

            print(f"[{i + 1:02}] {name}")

        selection = len(autograders) + 1

        while not (1 <= selection <= len(autograders)):
            try:
                selection = int(
                    input(f"Enter number corresponding to the autograder to run (1 - {len(autograders)}): "))
            except ValueError:
                selection = len(autograders) + 1

        self.print_info_message(f"Selecting autograder config located at '{autograders[selection - 1]}'")
        return autograders[selection - 1]

    def configure_options(self):
        # currently no extra options
        self.parser.add_argument("--submission-directory", default="student_work",
                                 help="The location for the student's submission relative to the submission root")
        self.parser.add_argument("--test-directory", default="student_tests",
                                 help="The location for the tests for the autograder relative to the submission root")

    def set_config_arguments(self, configBuilder: AutograderConfigurationBuilder[AutograderConfiguration]):
        pass

    def run(self) -> bool:
        self.configure_options()

        self.arguments = self.parser.parse_args()

        self.config_location = os.path.abspath(self.arguments.config_file) if \
            os.path.exists(self.arguments.config_file) else self.select_root()

        if self.config_location is None:
            self.print_error_message(self.ENVIRONMENT_ERROR, "Failed to load autograder!")
            return False

        root_directory = os.path.dirname(self.config_location)

        self.print_info_message(f"Running autograder from '{root_directory}'")

        if not self.verify_student_work_present(os.path.join(root_directory, self.arguments.submission_directory)):
            return False

        fileChanged = self.verify_file_changed(os.path.join(root_directory, self.arguments.submission_directory))

        self.config = AutograderConfigurationBuilder() \
            .fromTOML(self.config_location) \
            .setStudentSubmissionDirectory(os.path.join(root_directory, self.arguments.submission_directory)) \
            .setTestDirectory(os.path.join(root_directory, self.arguments.test_directory)) \
            .build()

        AutograderConfigurationProvider.set(self.config)

        self.discover_tests()

        self.print_info_message("Starting autograder")

        runner = BetterPyUnitFormat.BetterPyUnitTestRunner()

        res = runner.run(self.tests)

        if not fileChanged:
            self.print_warning_message("Student Submission Warning", "Student's submission may not have changed!")

        return res.wasSuccessful()


tool = LocalAutograderCLI().run

if __name__ == "__main__":
    res = tool()

    if res:
        exit(0)

    exit(1)
