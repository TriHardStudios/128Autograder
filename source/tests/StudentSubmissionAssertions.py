from StudentSubmission import StudentSubmission


class StudentSubmissionAssertions:
    def assertSubmissionValid(self):
        pass


class StudentSubmissionStdIOAssertions(StudentSubmissionAssertions):

    def assertSubmissionExecution(self, _studentSubmission: StudentSubmission,
                                  _stdin: list[str], _stdout: list[str],
                                  _timeout: int):

        status, stdout = _studentSubmission.runMainModule(_stdin, _timeout)

        if not status:
            stdout = [error for error in stdout if 'output' not in error.lower()]
            msg: str = "Failed to execute student submission."

            if stdout:
                stdout += " Error(s):\n"
                for error in stdout:
                    stdout += error + "\n"

            raise AssertionError(msg)
