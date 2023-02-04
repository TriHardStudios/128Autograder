from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner
import unittest

def main():
    testSuite = unittest.defaultTestLoader.discover("/autograder/source/tests")
    with open("/autograder/results/results.json", 'w+') as results:
        JSONTestRunner(visibility='visible', stream=results).run(testSuite);

if __name__ == "__main__":
    main()
