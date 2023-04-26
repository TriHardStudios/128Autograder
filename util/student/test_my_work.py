import sys
import os
import subprocess

def verfiyRequiredPackages() -> bool:
    errorOccured: bool = False

    try:
        import BetterPyUnitFormat
    except ModuleNotFoundError:
        print("[Required Package Error] BetterPyUnitFormat was not found. Please ensure that you have run 'pip install Better-PyUnit-Format'")
        errorOccured = True

    try:
        import gradescope_utils
    except ModuleNotFoundError:
        print("[Required Package Error] Gradescope Utils was not found. Please ensure that you have run 'pip install gradescope-utils'")
        errorOccured = True

    return not errorOccured

def verifyStudentWorkPresent(_submissionDirectory: str) -> bool:
    if not os.path.exists(_submissionDirectory):
        print(f"[Student Submission Error] Failed to locate student work in {_submissionDirectory}")
        return False

    if not os.path.isdir(_submissionDirectory):
        print(f"[Student Submission Error] submissionDirectoy is not a directory.")
        return False

    if len(os.listdir(_submissionDirectory)) < 2:
        print(f"[Student Submission Error] no valid files found in submission directory. Found {os.listdir(_submissionDirectory)}")
        return False

    return True


if __name__ == "__main__":
    submissionDirectory = "student_work"

    if len(sys.argv) == 2:
        submissionDirectory = sys.argv[1]

    if not verfiyRequiredPackages():
        sys.exit(1)

    if not verifyStudentWorkPresent(submissionDirectory):
        sys.exit(1)

    command: list[str] = ["python3", "run.py", "--unit-test-only", submissionDirectory]


    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end="")



