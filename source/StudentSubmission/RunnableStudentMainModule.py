import threading


class RunnableStudentMainModule(threading.Thread):

    def __init__(self, _compiledStudentCode):
        super().__init__(name="Student Submission")
        self.code = _compiledStudentCode
        self.runtimeException: Exception | None = None

    def run(self):
        try:
            exec(self.code, {'__name__': "__main__"})
        except Exception as g_ex:
            self.runtimeException = g_ex

    def join(self, timeout: float | None = ...):
        threading.Thread.join(self, timeout)

        if self.runtimeException:
            raise self.runtimeException

