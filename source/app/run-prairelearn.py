from autograder_utils.ResultBuilders import prairieLearnResultBuilder
from autograder_utils.ResultFinalizers import prairieLearnResultFinalizer
from autograder_utils.JSONTestRunner import JSONTestRunner

# CLI tools should only be able to import from the CLI part of the library
from autograder_platform.cli import AutograderCLITool
from autograder_platform.config.Config import AutograderConfigurationBuilder, AutograderConfiguration


class PrairieLearnAutograderCLI(AutograderCLITool):
    def __init__(self):
        super().__init__("PrairieLearn")

    def configure_options(self):
        self.parser.add_argument("--results-location", default="/grade/results/results.json",
                                 help="The location for the autograder JSON results")
        self.parser.add_argument("--metadata-path", default="/grade/data/data.json",
                                 help="The location for the submission metadata JSON")
        self.parser.add_argument("--submission-directory", default="/grade/submission",
                                 help="The directory where the student's submission is located")

    def set_config_arguments(self, configBuilder: AutograderConfigurationBuilder[AutograderConfiguration]):
        if self.arguments is None:
            return

        configBuilder.setStudentSubmissionDirectory(self.arguments.submission_directory)

    def run(self) -> bool:
        self.load_config()

        if self.arguments is None:
            return False

        self.discover_tests()

        with open(self.arguments.results_location, 'w') as w:
            testRunner = JSONTestRunner(visibility='visible', stream=w,
                                        result_builder=prairieLearnResultBuilder,
                                        result_finalizer=prairieLearnResultFinalizer)

            res = testRunner.run(self.tests)

            return res.wasSuccessful()


if __name__ == "__main__":
    tool = PrairieLearnAutograderCLI()

    res = tool.run()

    if res:
        exit(0)

    exit(1)
