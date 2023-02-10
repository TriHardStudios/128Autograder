import sys

from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner
from TestingFramework import TestRegister


def main(_resultsPath: str):
    testSuite = TestRegister()
    with open(_resultsPath, 'w+') as results:
        testRunner = JSONTestRunner(visibility='visible', stream=results)
        testRunner.run(testSuite)


if __name__ == "__main__":
    resultsPath: str = "/autograder/results/results.json"
    if len(sys.argv) == 2 and sys.argv[1] == "--local":
        resultsPath = "../student/results/results.json"

    main(resultsPath)
