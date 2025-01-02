import abc
import argparse
import unittest.loader
from argparse import ArgumentParser
from typing import List, Callable, Dict, Optional
from unittest import TestSuite

from autograder_platform.config.Config import AutograderConfigurationBuilder, AutograderConfigurationProvider, \
    AutograderConfiguration

def buildCommonOptions() -> argparse.ArgumentParser:
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

    return parser



def loadConfig(args: List[str], cliParser: argparse.ArgumentParser):
    """
    This function creates an autograder config given a CLI
    """
    parsed_args = cliParser.parse_args(args)

    # load toml then override any options in toml with things that are passed to the runtime
    autograderConfig = AutograderConfigurationBuilder()\
        .fromTOML(file=parsed_args.config_file)\
        .fromArgs(vars(parsed_args))\
        .build()

    AutograderConfigurationProvider.set(autograderConfig)

def discoverTests() -> TestSuite:
    config = AutograderConfigurationProvider.get()

    tests = unittest.loader.defaultTestLoader.discover(config.config.test_directory)

    return tests


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


class AutograderCLITool(abc.ABC):

    PACKAGE_ERROR: str = "Required Package Error"
    SUBMISSION_ERROR: str = "Student Submission Error"
    ENVIRONMENT_ERROR: str = "Environment Error"
    RED_COLOR: str = u"\u001b[31m"
    YELLOW_COLOR: str = u"\u001b[33m"
    BLUE_COLOR: str = u"\u001b[34m"
    RESET_COLOR: str = u"\u001b[0m"

    @classmethod
    def print_error_message(cls, errorType: str, errorText: str) -> None:
        """
        This function prints out a validation error message as they occur.
        The error type is colored red when it is printed
        the format used is `[<error_type>] <error_text>`
        :param errorType: The error type
        :param errorText: the text for the error
        :return:
        """
        print(f"[{cls.RED_COLOR}{errorType}{cls.RESET_COLOR}]: {errorText}")


    @classmethod
    def print_warning_message(cls, warningType: str, warningText: str) -> None:
        print(f"[{cls.YELLOW_COLOR}{warningType}{cls.RESET_COLOR}]: {warningText}")

    @classmethod
    def print_info_message(cls, text: str) -> None:
        print(f"[{cls.BLUE_COLOR}INFORMATION{cls.RESET_COLOR}]: {text}")

    def __init__(self, tool_name: str):
        self.config: Optional[AutograderConfiguration] = None
        self.arguments: Optional[argparse.Namespace] = None
        self.tests: Optional[TestSuite] = None

        self.parser: ArgumentParser = argparse.ArgumentParser(description=f"Autograder Platform - {tool_name}")

        # required CLI arguments
        self.parser.add_argument("--config-file", default="./config.toml",
                            help="Set the location of the config file")

    @abc.abstractmethod
    def configure_options(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def set_config_arguments(self, configBuilder: AutograderConfigurationBuilder[AutograderConfiguration]):
        raise NotImplementedError()

    @abc.abstractmethod
    def run(self) -> bool:
        raise NotImplementedError()

    def load_config(self):
        self.arguments = self.parser.parse_args()

        # load toml then override any options in toml with things that are passed to the runtime
        builder = AutograderConfigurationBuilder() \
            .fromTOML(file=self.arguments.config_file)

        self.set_config_arguments(builder)

        self.config = builder.build()

        AutograderConfigurationProvider.set(self.config)

    def discover_tests(self):
        self.tests = unittest.loader.defaultTestLoader.discover(self.config.config.test_directory)

