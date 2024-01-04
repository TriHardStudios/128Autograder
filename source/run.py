import sys
import unittest
from unittest.suite import TestSuite
from utils.config.Config import AutograderConfigurationBuilder, AutograderConfigurationProvider
from utils.Gradescope import gradescopePostProcessing
import argparse

def processArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CSCI 128 Autograder Platform")

    parser.add_argument("--unit-test-only", action="store_true",
                        help="Only run the unit tests associated with this autograder")

    parser.add_argument("--test-directory", default=None,
                        help="Set the test directory")

    parser.add_argument("--config-file", default="./config.toml", 
                        help="Set the location of the config file")

    options, remaining = parser.parse_known_args()
    
    options.submission_directory = "/autograder/submission"
    
    if options.unit_test_only:
        parser.add_argument("--submission-directory", required=True,
                            help="Set the directory for the student's submission")

    options = parser.parse_args(args=remaining, namespace=options)

    return options

def main():
    options = processArgs()

    resultsPath: str = "/autograder/results/results.json"
    METADATA_PATH = "/autograder/submission_metadata.json"

    autograderConfig = AutograderConfigurationBuilder()\
        .fromTOML(file=options.config_file)\
        .setStudentSubmissionDirectory(options.submission_directory)\
        .setTestDirectory(options.test_directory)\
        .build()

    AutograderConfigurationProvider.set(autograderConfig)

    tests = unittest.loader.defaultTestLoader\
                    .discover(autograderConfig.config.test_directory)

    if options.unit_test_only:
        from BetterPyUnitFormat.BetterPyUnitTestRunner import BetterPyUnitTestRunner
        testRunner = BetterPyUnitTestRunner()
        testRunner.run(tests)
        return

    with open(resultsPath, 'w') as results:
        from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner
        testRunner = JSONTestRunner(visibility='visible',
                                    stream=results,
                                    post_processor=lambda resultsDict: gradescopePostProcessing(resultsDict, autograderConfig, METADATA_PATH))
        testRunner.run(tests)


if __name__ == "__main__":
    main()
