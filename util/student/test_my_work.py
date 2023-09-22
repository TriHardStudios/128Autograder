import sys
import os
import re
import subprocess
import json
import hashlib

PACKAGE_ERROR: str = "Required Package Error"
SUBMISSION_ERROR: str = "Student Submission Error"
RED_COLOR: str = u"\u001b[31m"
YELLOW_COLOR: str = u"\u001b[33m"
RESET_COLOR: str = u"\u001b[0m"
SUBMISSION_REGEX: re.Pattern = re.compile(r"^(\w|\s)+\.py$")
FILE_HASHES_NAME: str = ".filehashes" 


def printErrorMessage(_errorType: str, _errorText: str) -> None:
    """
    This function prints out a validation error message as they occur.
    The error type is colored red when it is printed
    the format used is `[<error_type>] <error_text>`
    :param _errorType: The error type
    :param _errorText: the text for the error
    :return:
    """
    print(f"[{RED_COLOR}{_errorType}{RESET_COLOR}]: {_errorText}")


def printWarningMessage(_warningType: str, _warningText: str) -> None:
    print(f"[{YELLOW_COLOR}{_warningType}{RESET_COLOR}]: {_warningText}")

def verifyRequiredPackages() -> bool:
    """
    This function verifies that all the required packages needed for the actual autograder are installed
    :return: true if they are false if not.
    """
    errorOccurred: bool = False

    try:
        import BetterPyUnitFormat
    except ModuleNotFoundError:
        printErrorMessage(PACKAGE_ERROR,
                          "BetterPyUnitFormat was not found. "
                          "Please ensure that you have run 'pip install Better-PyUnit-Format'")
        errorOccurred = True

    try:
        import gradescope_utils
    except ModuleNotFoundError:
        printErrorMessage(PACKAGE_ERROR,
                          "Gradescope Utils was not found. "
                          "Please ensure that you have run 'pip install gradescope-utils'")
        errorOccurred = True

    try:
        import dill
    except ModuleNotFoundError:
        printErrorMessage(PACKAGE_ERROR,
                          "Dill was not found. "
                          "Please ensure that you have run 'pip install dill'")
        errorOccurred = True

    return not errorOccurred


def verifyStudentWorkPresent(_submissionDirectory: str) -> bool:
    """
    This function verifies that the student has work in the submission directory
    :param _submissionDirectory: the directory that the student did their work in.
    :return: true if the student has work present
    """

    if not os.path.exists(_submissionDirectory):
        printErrorMessage(SUBMISSION_ERROR, f"Failed to locate student work in {_submissionDirectory}")
        return False

    if not os.path.isdir(_submissionDirectory):
        printErrorMessage(SUBMISSION_ERROR, f"{_submissionDirectory} is not a directory.")
        return False

    # this doesn't catch files in folders. Something to be aware of for students
    files = [file for file in os.listdir(_submissionDirectory) if SUBMISSION_REGEX.match(file)]

    if len(files) < 1:
        printErrorMessage(SUBMISSION_ERROR,
                          f"No valid files found in submission directory. "
                          f"Found {os.listdir(_submissionDirectory)}")
        return False

    return True

def cleanPreviousSubmissions(_directory: str) -> None:
    """
    This function cleans out previous submissions if they exist.
    :param _directory: the directory to run the detection in.
    """
    zipFiles = [os.path.join(_directory, file) for file in os.listdir(_directory) if file[-4:] == ".zip"]
    if len(zipFiles) > 0:
        print("Previous submissions found. Cleaning out old submission files...")
        for file in zipFiles:
            print(f"\tRemoving {file}...")
            os.remove(file)


def generateHashes(_submissionDirectory: str) -> dict[str, str]:
    """
    This function generates hashes for the files in submission directory.

    :param _submissionDirectory: The directory to base all the hashes out of
    """

    pythonFiles = [
             os.path.join(_submissionDirectory, file) 
             for file in os.listdir(_submissionDirectory) 
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


def verifyFileChanged(_submissionDirectory: str) -> bool:
    """
    This function checks to see if a file has changed since the last run of this script.

    It stores its results in `_submissionDirectory/.filehashes`. Currently it does not support sub directories.

    :param _submissionDirectory: the directory that the student is doing their work in.

    :return: true if at least of the files changed.

    """

    FILE_HASHES_PATH = os.path.join(_submissionDirectory, FILE_HASHES_NAME)

    if not os.path.exists(FILE_HASHES_PATH):
        with open(FILE_HASHES_PATH, 'w') as w:
            json.dump({}, w)


    with open(FILE_HASHES_PATH, 'r') as r:
        existingHashes = json.load(r)

    newHashes = generateHashes(_submissionDirectory)

    
    with open(FILE_HASHES_PATH, 'w') as w:
        json.dump(newHashes, w)


    return existingHashes != newHashes


if __name__ == "__main__":
    cleanPreviousSubmissions(".")

    submissionDirectory = "student_work/"

    if len(sys.argv) == 2:
        submissionDirectory = sys.argv[1]

    # need to make sure to that we have a / at the end of the path
    if submissionDirectory[-1:] != '/':
        submissionDirectory += "/"

    if not verifyRequiredPackages():
        sys.exit(1)

    if not verifyStudentWorkPresent(submissionDirectory):
        sys.exit(1)

    if not verifyFileChanged(submissionDirectory):
        printWarningMessage("Student Submission Warning", "Student submision may not have changed")

    command: list[str] = [sys.executable, "run.py", "--unit-test-only", submissionDirectory]

    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end="")
