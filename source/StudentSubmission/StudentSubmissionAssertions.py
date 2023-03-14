from .StudentSubmission import StudentSubmission


class StudentSubmissionAssertions:
    def assertSubmissionValid(self, _studentSubmission: StudentSubmission):
        if not _studentSubmission.isSubmissionValid():
            raise AssertionError(_studentSubmission.getValidationError())


class StudentSubmissionStdIOAssertions(StudentSubmissionAssertions):

    def assertSubmissionExecution(self, _studentSubmission: StudentSubmission,
                                  _stdin: list[str], _stdout: list[str],
                                  _timeout: int):

        status, stdout = _studentSubmission.runMainModule(_stdin, _timeout)

        if not status:
            stdout = [error for error in stdout if 'output' not in error.lower()]
            msg: str = "Failed to execute student submission."

            if stdout:
                msg += " Error(s):\n"
                for error in stdout:
                    msg += error + "\n"

            raise AssertionError(msg)

        _stdout.extend(stdout)

    def assertCorrectNumberOfOutputLines(self, expected: list[str], actual: list[str]):
        if len(actual) == 0:
            raise AssertionError("No OUTPUT lines found. Check OUTPUT formatting.")

        if len(actual) > len(expected):
            raise AssertionError(f"Too many OUTPUT lines. Check OUTPUT formatting.\n"
                                 f"Expected number of lines: {len(expected)}\n"
                                 f"Actual number of lines  : {len(actual)}")

        if len(actual) < len(expected):
            raise AssertionError(f"Too few OUTPUT lines. Check OUTPUT formatting.\n"
                                 f"Expected number of lines: {len(expected)}\n"
                                 f"Actual number of lines  : {len(actual)}")
