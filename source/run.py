import unittest
import argparse
from lib.config import AutograderConfigurationBuilder, AutograderConfigurationProvider
from utils.Gradescope import gradescopePostProcessing
from autograder_utils.JSONTestRunner import JSONTestRunner
from autograder_utils.ResultFinalizers import prairieLearnResultFinalizer, gradescopeResultFinalizer
from autograder_utils.ResultBuilders import prairieLearnResultBuilder, gradescopeResultBuilder
from BetterPyUnitFormat.BetterPyUnitTestRunner import BetterPyUnitTestRunner




if __name__ == "__main__":
    options = processArgs()

    wasSuccessful = main(options)

    if wasSuccessful:
        exit(0)

    exit(1)
