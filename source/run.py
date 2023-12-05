import sys
from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner
from TestingFramework import TestRegister
from utils.config.Config import AutograderConfiguration, AutograderConfigurationBuilder
from utils import gradescopePostProcessing

def main(runUnitTestsOnly: bool, resultsPath: str, autograderConfiguration: AutograderConfiguration):
    testSuite = TestRegister()

    if runUnitTestsOnly:
        from BetterPyUnitFormat.BetterPyUnitTestRunner import BetterPyUnitTestRunner
        testRunner = BetterPyUnitTestRunner()
        testRunner.run(testSuite)
        return

    with open(resultsPath, 'w+') as results:
        testRunner = JSONTestRunner(visibility='visible',
                                    stream=results,
                                    post_processor=lambda resultsDict: gradescopePostProcessing(resultsDict, autograderConfiguration))
        testRunner.run(testSuite)


if __name__ == "__main__":
    resultsPath: str = "/autograder/results/results.json"
    if len(sys.argv) == 2 and sys.argv[1] == "--local":
        resultsPath = "../student/results/results.json"

    autograderConfig = AutograderConfigurationBuilder()\
        .fromTOML()\
        .build()

    main(len(sys.argv) == 3 and sys.argv[1] == "--unit-test-only", resultsPath, autograderConfig)
