import os.path
import sys

from autograder_utils.ResultBuilders import prairieLearnResultBuilder
from autograder_utils.ResultFinalizers import prairieLearnResultFinalizer
from autograder_utils.JSONTestRunner import JSONTestRunner

from autograder_platform.cli import loadConfig, buildCommonOptions, discoverTests, printErrorMessage, PACKAGE_ERROR

def getPrairieLearnResultsLocation() -> str:
    return os.path.join("/", "grade", "results", "results.json")

def getPrairieLearnMetadataLocation() -> str:
    return os.path.join("/", "grade", "data", "data.json")


def run():
    parser = buildCommonOptions()
    parser.description += " - PrairieLearn Deployment"

    loadConfig(sys.argv, parser)

    tests = discoverTests()

    with open(getPrairieLearnResultsLocation(), 'w') as w:
        testRunner = JSONTestRunner(visibility='visible', stream=w,
                                    result_builder=prairieLearnResultBuilder,
                                    result_finalizer=prairieLearnResultFinalizer)

        res = testRunner.run(tests)

        return res.wasSuccessful()


if __name__ == "__main__":
    res = run()

    if res:
        exit(0)

    exit(1)
