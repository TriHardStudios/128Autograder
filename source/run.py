import os

from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner
import unittest


def main(_testPath: str, _resultsPath: str):
    testSuite = unittest.defaultTestLoader.discover(_testPath)
    with open(_resultsPath, 'w+') as results:
        testRunner = JSONTestRunner(visibility='visible', stream=results)
        testRunner.run(testSuite)


if __name__ == "__main__":
    testPath: str = "/autograder/source/tests"
    resultsPath: str = "/autograder/results/results.json"
    if not os.getenv("RUNNING_IN_AUTOGRADER"):
        testPath = "tests"
        resultsPath = "../student/results/results.json"

    main(testPath, resultsPath)
