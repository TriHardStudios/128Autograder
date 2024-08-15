import sys
import os
import re
import subprocess
import json
import importlib.util
import hashlib
from typing import Dict, Tuple

PACKAGE_ERROR: str = "Required Package Error"
SUBMISSION_ERROR: str = "Student Submission Error"
ENVIRONMENT_ERROR: str = "Environment Error"
RED_COLOR: str = u"\u001b[31m"
YELLOW_COLOR: str = u"\u001b[33m"
RESET_COLOR: str = u"\u001b[0m"
SUBMISSION_REGEX: re.Pattern = re.compile(r"^(\w|\s)+\.py$")
FILE_HASHES_NAME: str = ".filehashes"
MIN_VERSION = (3, 11)

REQUIRED_PACKAGES = {
    "autograder_utils": "git+https://github.com/gregbell26/HybridJsonTestRunner@0.7.0",
    "dill": "dill",
    "BetterPyUnitFormat": "Better-PyUnit-Format",
    "schema": "schema",
    "requests": "requests",
    "tomli": "tomli"
}


def printErrorMessage(errorType: str, errorText: str) -> None:
    """
    This function prints out a validation error message as they occur.
    The error type is colored red when it is printed
    the format used is `[<error_type>] <error_text>`
    :param errorType: The error type
    :param errorText: the text for the error
    :return:
    """
    print(f"[{RED_COLOR}{errorType}{RESET_COLOR}]: {errorText}")


def printWarningMessage(warningType: str, warningText: str) -> None:
    print(f"[{YELLOW_COLOR}{warningType}{RESET_COLOR}]: {warningText}")


def verifyRequiredPackages(packagesToVerify: Dict[str, str]) -> bool:
    """
    This function verifies that all the required packages needed for the actual autograder are installed
    :return: true if they are false if not.
    """
    errorOccurred: bool = False

    for name, package in packagesToVerify.items():
        if importlib.util.find_spec(name) is None:
            print(f"Installing missing dependency: {package}...", end="")
            subprocess.run([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL)
            print(f"Done.")

    return not errorOccurred


def verifyStudentWorkPresent(submissionDirectory: str) -> bool:
    """
    This function verifies that the student has work in the submission directory
    :param submissionDirectory: the directory that the student did their work in.
    :return: true if the student has work present
    """

    if not os.path.exists(submissionDirectory):
        printErrorMessage(SUBMISSION_ERROR, f"Failed to locate student work in {submissionDirectory}")
        return False

    # this doesn't catch files in folders. Something to be aware of for students
    files = [file for file in os.listdir(submissionDirectory) if SUBMISSION_REGEX.match(file)]

    if len(files) < 1:
        printErrorMessage(SUBMISSION_ERROR,
                          f"No valid files found in submission directory. "
                          f"Found {os.listdir(submissionDirectory)}")
        return False

    return True


def cleanPreviousSubmissions(directory: str) -> None:
    """
    This function cleans out previous submissions if they exist.
    :param directory: the directory to run the detection in.
    """
    zipFiles = [os.path.join(directory, file) for file in os.listdir(directory) if file[-4:] == ".zip"]
    if len(zipFiles) > 0:
        print("Previous submissions found. Cleaning out old submission files...")
        for file in zipFiles:
            print(f"\tRemoving {file}...")
            os.remove(file)


def generateHashes(submissionDirectory: str) -> Dict[str, str]:
    """
    This function generates hashes for the files in submission directory.

    :param submissionDirectory: The directory to base all the hashes out of
    """

    pythonFiles = [
        os.path.join(submissionDirectory, file)
        for file in os.listdir(submissionDirectory)
        if SUBMISSION_REGEX.match(file)
    ]

    fileHashes: dict[str, str] = {}

    for file in pythonFiles:
        with open(file, 'rb') as r:
            # technically this can lead to overflow issues if the file is too large. 
            #  That shouldnt happen in this class hopefully
            fileBytes = r.read()
            fileHashes[file] = hashlib.md5(fileBytes, usedforsecurity=False).hexdigest()

    return fileHashes


def verifyFileChanged(submissionDirectory: str) -> bool:
    """
    This function checks to see if a file has changed since the last run of this script.

    It stores its results in `submissionDirectory/.filehashes`. Currently it does not support sub directories.

    :param submissionDirectory: the directory that the student is doing their work in.

    :return: true if at least of the files changed.

    """

    FILE_HASHES_PATH = os.path.join(submissionDirectory, FILE_HASHES_NAME)

    if not os.path.exists(FILE_HASHES_PATH):
        with open(FILE_HASHES_PATH, 'w') as w:
            json.dump({}, w)

    with open(FILE_HASHES_PATH, 'r') as r:
        try:
            existingHashes = json.load(r)
        except json.JSONDecodeError:
            existingHashes = None

    newHashes = generateHashes(submissionDirectory)

    with open(FILE_HASHES_PATH, 'w') as w:
        json.dump(newHashes, w)

    return existingHashes != newHashes


def verifyPythonVersion(minVersion: Tuple[int, int], pythonVersionTuple: Tuple[int, int, int, str, int]) -> bool:
    if minVersion[0] != pythonVersionTuple[0] or minVersion[1] > pythonVersionTuple[1]:
        printErrorMessage(ENVIRONMENT_ERROR, f"Unsupported Python Version. Expected Python >= {minVersion[0]}.{minVersion[1]}. Was {pythonVersionTuple[0]}.{pythonVersionTuple[1]}.{pythonVersionTuple[2]}")
        return False

    return True


if __name__ == "__main__":
    if not verifyPythonVersion(MIN_VERSION, sys.version_info):  # type: ignore
        sys.exit(1)

    cleanPreviousSubmissions(".")

    submissionDirectory = sys.argv[1] if len(sys.argv) == 2 else "student_work/"

    if not verifyRequiredPackages(REQUIRED_PACKAGES):
        sys.exit(1)

    if not verifyStudentWorkPresent(submissionDirectory):
        sys.exit(1)

    fileChanged: bool = verifyFileChanged(submissionDirectory)

    command: list[str] = [sys.executable, "run.py", "--unit-test-only", "--submission-directory", submissionDirectory]

    subprocess.run(command)

    if not fileChanged:
        printWarningMessage("Student Submission Warning", "Student submision may not have changed")
