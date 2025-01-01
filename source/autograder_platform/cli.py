import argparse
from typing import List, Callable, Dict

from autograder_platform.config.Config import AutograderConfigurationBuilder, AutograderConfigurationProvider


def buildCommonOptions() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CSCI 128 Autograder Platform")

    parser.add_argument("--build", action="store_true",
                        help="Build Autograder according to config file")

    parser.add_argument("--source", default=".",
                        help="The source directory of the autograder that is being built")

    parser.add_argument("-o", default="bin",
                        help="The output folder for build")

    parser.add_argument("--unit-test-only", action="store_true",
                        help="Only run the unit tests associated with this autograder")

    parser.add_argument("--test-directory", default=None,
                        help="Set the test directory")

    parser.add_argument("--config-file", default="./config.toml",
                        help="Set the location of the config file")

    parser.add_argument("--submission-directory", default="/autograder/submission",
                        help="Set the directory for the student's submission")

    parser.add_argument("--deployed-environment", choices=["gradescope", "prairie_learn", ],
                        default="gradescope",
                        help="The deployment environment that the autograder is configured for")

    parser.add_argument("--results-path", default="/autograder/results/results.json",
                        help="The path that the autograder should store JSON results at")

    parser.add_argument("--metadata-path", default="/autograder/submission_metadata.json",
                        help="The path that the autograder should read submission metadata from")

    options = parser.parse_args()

    if options.build:
        options.submission_directory = "."

    return options


def load_config(args: List[str], cli_parser: argparse.ArgumentParser):
    """
    This function creates an autograder config given a CLI
    """
    parsed_args = cli_parser.parse_args(args)

    # load toml then override any options in toml with things that are passed to the runtime
    autograderConfig = AutograderConfigurationBuilder()\
        .fromTOML(file=parsed_args.config_file)\
        .fromArgs(vars(parsed_args))\
        .build()

    AutograderConfigurationProvider.set(autograderConfig)


def main(options: argparse.Namespace):
    autograderConfig = AutograderConfigurationBuilder() \
        .fromTOML(file=options.config_file) \
        .setStudentSubmissionDirectory(options.submission_directory) \
        .setTestDirectory(options.test_directory) \
        .build()

    if options.build:
        from utils.Build import Build
        build = Build(autograderConfig, sourceRoot=options.source, binRoot=options.o)
        build.build()
        return True

    # Only need to set the provider if we are running tests
    AutograderConfigurationProvider.set(autograderConfig)

    tests = unittest.loader.defaultTestLoader \
        .discover(autograderConfig.config.test_directory)

    if options.unit_test_only:
        testRunner = BetterPyUnitTestRunner()
        res = testRunner.run(tests)
        return res.wasSuccessful()

    testResultBuilder = gradescopeResultBuilder
    resultFinalizer = gradescopeResultFinalizer
    postProcessor = lambda resultsDict: gradescopePostProcessing(resultsDict,
                                                                 autograderConfig,
                                                                 options.metadata_path)
    if options.deployed_environment == "prairie_learn":
        testResultBuilder = prairieLearnResultBuilder
        resultFinalizer = prairieLearnResultFinalizer
        postProcessor = lambda _: None

    with open(options.results_path, 'w') as results:
        testRunner = JSONTestRunner(visibility='visible',
                                    stream=results,
                                    post_processor=postProcessor,
                                    result_builder=testResultBuilder, result_finalizer=resultFinalizer)
        res = testRunner.run(tests)
        return res.wasSuccessful()
