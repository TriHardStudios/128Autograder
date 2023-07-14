import sys
import os
import subprocess

PACKAGE_ERROR: str = "Required Package Error"
SUBMISSION_ERROR: str = "Student Submission Error"
RED_COLOR: str = u"\u001b[31m"
RESET_COLOR: str = u"\u001b[0m"


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

    if len(os.listdir(_submissionDirectory)) < 2:
        printErrorMessage(SUBMISSION_ERROR,
                          f"No valid files found in submission directory. "
                          f"Found {os.listdir(_submissionDirectory)}")
        return False

    return True


if __name__ == "__main__":
    zipFiles = [file for file in os.listdir('.') if file[:-4] == ".zip"]
    if len(zipFiles) > 0:
        print("Previous submissions found. Cleaning out old submission files...")
        for file in zipFiles:
            print(f"\tRemoving {file}...")
            os.remove(file)

    submissionDirectory = "student_work/"

    if len(sys.argv) == 2:
        submissionDirectory = sys.argv[1]

    # need to make sure to that we have a / at the end of the path
    if submissionDirectory[:-1] != '/':
        submissionDirectory += "/"

    if not verifyRequiredPackages():
        sys.exit(1)

    if not verifyStudentWorkPresent(submissionDirectory):
        sys.exit(1)

    command: list[str] = ["python3", "run.py", "--unit-test-only", submissionDirectory]

    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end="")
