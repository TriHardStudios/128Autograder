
from common import Runner


class MainModuleRunner(Runner):
    def run(self):
        exec(self.studentSubmissionCode, {__name__: "__main__"}, {})
