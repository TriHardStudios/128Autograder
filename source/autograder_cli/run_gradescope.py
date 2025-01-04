import json
import os
from typing import Dict, List

from autograder_utils.ResultBuilders import gradescopeResultBuilder
from autograder_utils.ResultFinalizers import gradescopeResultFinalizer
from autograder_utils.JSONTestRunner import JSONTestRunner

# CLI tools should only be able to import from the CLI part of the library
from autograder_platform.cli import AutograderCLITool
from autograder_platform.config.Config import AutograderConfigurationBuilder, AutograderConfiguration


class GradescopeAutograderCLI(AutograderCLITool):
    def __init__(self):
        super().__init__("Gradescope")

    def gradescope_post_processing(self, autograderResults: Dict):
        if not os.path.exists(self.arguments.metadata_path):
            return

        if "tests" not in autograderResults or len(autograderResults["tests"]) == 0:
            autograderResults['output'] = "No tests were run. If you are a student seeing this message, please notify course staff."
            return

        # for now, we aren't implementing any new features for this
        submissionLimit = self.config.config.submission_limit
        takeHighest = self.config.config.take_highest

        # Enforce submission limit
        submissionMetadata: Dict = {}
        with open(self.arguments.metadata_path, 'r') as submissionMetadataIn:
            submissionMetadata = json.load(submissionMetadataIn)

        previousSubmissions: List[Dict] = submissionMetadata['previous_submissions']

        autograderResults['output'] = f"Submission {len(previousSubmissions) + 1} of {submissionLimit}.\n"

        validSubmissions: List[Dict] = \
            [previousSubmissionMetadata['results']
             for previousSubmissionMetadata in previousSubmissions
             if 'results' in previousSubmissionMetadata.keys()
             ]

        validSubmissions.append(autograderResults)

        # submission limit exceeded
        if len(validSubmissions) > submissionLimit:
            autograderResults['output'] += f"Submission limit exceeded.\n" \
                                           f"Autograder has been run on your code so you can see how you did\n" \
                                           f"but, your score will be highest of your valid submissions.\n"
            validSubmissions = validSubmissions[:submissionLimit]
            # We should take the highest valid submission
            takeHighest = True
        # TODO drop all un-scored submissions

        # sorts in descending order
        validSubmissions.sort(reverse=True, key=lambda submission: submission['score'] if 'score' in submission else 0)

        if takeHighest and validSubmissions[0] != autograderResults:
            autograderResults['output'] += f"Score has been set to your highest valid score.\n"
            autograderResults['score'] = validSubmissions[0]['score']

        # ensure that negative scores arent possible
        if autograderResults['score'] < 0:
            autograderResults['output'] += f"Score has been set to a floor of 0 to ensure no negative scores.\n"
            autograderResults['score'] = 0

    def configure_options(self):  # pragma: no cover
        self.parser.add_argument("--results-location", default="/autograder/results/results.json",
                                 help="The location for the autograder JSON results")
        self.parser.add_argument("--metadata-path", default="submission_metadata.json",
                                 help="The location for the submission metadata JSON")
        self.parser.add_argument("--submission-directory", default="/autograder/submission",
                                 help="The directory where the student's submission is located")

    def set_config_arguments(self, configBuilder: AutograderConfigurationBuilder[AutograderConfiguration]):  # pragma: no cover
        if self.arguments is None:
            return

        configBuilder.setStudentSubmissionDirectory(self.arguments.submission_directory)

    def run(self) -> bool:  # pragma: no cover
        self.configure_options()

        self.load_config()

        if self.arguments is None:
            return True

        self.discover_tests()

        with open(self.arguments.results_location, 'w') as w:
            testRunner = JSONTestRunner(visibility='visible', stream=w,
                                        result_builder=gradescopeResultBuilder,
                                        result_finalizer=gradescopeResultFinalizer,
                                        post_processor=lambda results: self.gradescope_post_processing(results))

            res = testRunner.run(self.tests)

            return not res.wasSuccessful()


tool = GradescopeAutograderCLI().run

if __name__ == "__main__":
    res = tool()

    exit(res)

