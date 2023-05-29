import unittest

from StudentSubmission.RunnableStudentSubmission import RunnableStudentSubmission
from StudentSubmission.Runners import MainModuleRunner, FunctionRunner
from StudentSubmission.common import PossibleResults


class TestRunnableStudentSubmission(unittest.TestCase):

    def testStdIO(self):
        program = \
            ("\n"
             "userIn = input()\n"
             "print(userIn)\n")

        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_program", "exec"))

        strInput = ["this is input"]
        runnableSubmission = RunnableStudentSubmission(strInput, runner, 1)
        runnableSubmission.run()

        results = runnableSubmission.createResults()

        self.assertEqual(strInput, results[PossibleResults.STDOUT])

    def testFunctionStdIO(self):
        program = \
            ("\n"
             "def runMe():\n"
             "  userIn = input()\n"
             "  print(userIn)\n"
             )

        runner = FunctionRunner("runMe")
        runner.setSubmission(compile(program, "test_code", "exec"))
        strInput = ["this is input"]
        runnableSubmission = RunnableStudentSubmission(strInput, runner, 1)
        runnableSubmission.run()

        results = runnableSubmission.createResults()

        self.assertEqual(strInput, results[PossibleResults.STDOUT])

    def testFunctionParameterStdIO(self):
        program = \
            ("\n"
             "def runMe(value: str):\n"
             "  print(value)\n"
             )

        strInput = "this was passed as a parameter"
        runner = FunctionRunner("runMe", strInput)
        runner.setSubmission(compile(program, "test_code", "exec"))

        runnableSubmission = RunnableStudentSubmission([], runner, 1)
        runnableSubmission.run()

        results = runnableSubmission.createResults()

        self.assertEqual([strInput], results[PossibleResults.STDOUT])

    def testFunctionParameterReturn(self):
        program = \
            ("\n"
             "def runMe(value: int):\n"
             "  return value\n"
             )

        intInput = 128
        runner = FunctionRunner("runMe", intInput)
        runner.setSubmission(compile(program, "test_code", "exec"))
        runnableSubmission = RunnableStudentSubmission([], runner, 1)
        runnableSubmission.run()

        results = runnableSubmission.createResults()

        self.assertEqual(intInput, results[PossibleResults.RETURN_VAL])

