import unittest
from StudentSubmission.RunnableStudentSubmission import RunnableStudentSubmission
from StudentSubmission.Runners import MainModuleRunner, FunctionRunner
from StudentSubmission.common import PossibleResults, MissingOutputDataException, MissingFunctionDefinition
from TestingFramework import SingleFunctionMock


class TestRunnableStudentSubmission(unittest.TestCase):

    def testStdIO(self):
        program = \
            ("\n"
             "userIn = input()\n"
             "print(userIn)\n")

        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_code", "exec"))

        strInput = ["this is input"]
        runnableSubmission = RunnableStudentSubmission(strInput, runner, ".", 1)
        runnableSubmission.run()

        results = runnableSubmission.getOutputData()

        self.assertEqual(strInput, results[PossibleResults.STDOUT])

    def testStdIOWithMain(self):
        program = \
            "if __name__ == '__main__':\n" \
            "   userIn = input()\n" \
            "   print(userIn)\n"

        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_code", "exec"))

        strInput = ["this is input"]
        runnableSubmission = RunnableStudentSubmission(strInput, runner, ".", 1)
        runnableSubmission.run()

        results = runnableSubmission.getOutputData()

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
        runnableSubmission = RunnableStudentSubmission(strInput, runner, ".", 1)
        runnableSubmission.run()

        results = runnableSubmission.getOutputData()

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

        runnableSubmission = RunnableStudentSubmission([], runner, ".", 1)
        runnableSubmission.run()

        results = runnableSubmission.getOutputData()

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
        runnableSubmission = RunnableStudentSubmission([], runner, ".", 1)
        runnableSubmission.run()

        results = runnableSubmission.getOutputData()

        self.assertEqual(intInput, results[PossibleResults.RETURN_VAL])

    def testFunctionMock(self):
        program = \
            (
                "\n"
                "def mockMe(parm1, parm2, parm3):\n"
                "   pass\n"
                "\n"
                "def runMe():\n"
                "   mockMe(1, 2, 3)\n"
                "   mockMe(1, 2, 3)\n"
                "\n"
            )
        runner = FunctionRunner("runMe")
        runner.setSubmission(compile(program, "test_code", "exec"))
        runner.setMocks({"mockMe": SingleFunctionMock("mockMe", None)})

        runnableSubmission = RunnableStudentSubmission([], runner, ".", 1)
        runnableSubmission.run()

        results = runnableSubmission.getOutputData()
        mockMeMock: SingleFunctionMock = results[PossibleResults.MOCK_SIDE_EFFECTS]["mockMe"]

        mockMeMock.assertCalledWith(1, 2, 3)
        mockMeMock.assertCalledTimes(2)

    def testMissingFunctionDeclaration(self):
        program = \
            (
                "def ignoreMe():\n"
                "   return True\n"
            )

        runner = FunctionRunner("runMe")
        runner.setSubmission(compile(program, "test_code", "exec"))

        runnableSubmission = RunnableStudentSubmission([], runner, ".", 1)
        runnableSubmission.run()

        with self.assertRaises(MissingFunctionDefinition):
            raise runnableSubmission.getException()



    def testTerminateInfiniteLoop(self):
        program = \
            (
                "\n"
                "while True:\n"
                "   print('OUTPUT LOOP:)')\n"
                "\n"
            )
        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_code", "exec"))

        # run for 10 sec to overflow write buffer
        runnableSubmission = RunnableStudentSubmission([], runner, ".", 10)
        runnableSubmission.run()

        self.assertDictEqual({}, runnableSubmission.getOutputData())
        self.assertTrue(runnableSubmission.getTimeoutOccurred())

    def testTerminateInfiniteLoopWithInput(self):
        program = \
            (
                "import time\n"
                "\n"
                "while True:\n"
                "   time.sleep(.25)\n"
                "   var = input()\n"
                "   print(var)\n"
                "\n"
            )

        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_code", "exec"))

        runnableSubmission = RunnableStudentSubmission(("hello\n" * 9999).splitlines(), runner, ".", 5)
        runnableSubmission.run()

        self.assertDictEqual({}, runnableSubmission.getOutputData())
        self.assertTrue(runnableSubmission.getTimeoutOccurred())

    def testHandledExceptionInfiniteRecursion(self):
        program = \
            (
                "\n"
                "def loop():\n"
                "   print('OUTPUT RECURSION')\n"
                "   loop()\n"
                "\n"
                "loop()\n"
            )

        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_code", "exec"))

        runnableSubmission = RunnableStudentSubmission([], runner, ".", 5)
        runnableSubmission.run()

        with self.assertRaises(RecursionError):
            raise runnableSubmission.getException()

    def testHandledExceptionBlockedInput(self):
        program = \
            (
                "\n"
                "var1 = input()\n"
                "var2 = input()\n"
                "\n"
            )

        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_code", "exec"))

        runnableSubmission = RunnableStudentSubmission(["1"], runner, ".", 5)
        runnableSubmission.run()

        with self.assertRaises(EOFError):
            raise runnableSubmission.getException()

    def testHandleExit(self):
        program = \
            (
                "exit(0)"
            )

        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_code", "exec"))

        runnableSubmission = RunnableStudentSubmission([], runner, ".", 1)
        runnableSubmission.run()

        with self.assertRaises(MissingOutputDataException):
            raise runnableSubmission.getException()

    def testHandleManyFailedRuns(self):
        # This test enforces that we prefer a resource leak to crashing tests
        # This might need to be re-evaluated in the future
        program = \
            (
                "print('Hi Mom!')\n"
            )

        capturedCleanup = RunnableStudentSubmission.cleanup
        RunnableStudentSubmission.cleanup = lambda _: None

        runner = MainModuleRunner()
        runner.setSubmission(compile(program, "test_code", "exec"))

        runnableSubmission = RunnableStudentSubmission([], runner, ".", 1)
        runnableSubmission.run()

        runnableSubmission = RunnableStudentSubmission([], runner, ".", 1)

        RunnableStudentSubmission.cleanup = capturedCleanup

        runnableSubmission.run()


    def testImportedFunction(self):
        program = \
            "import random\n"\
            "def test():\n"\
            "    random.seed('autograder')\n"\
            "    return random.randint(0, 5)\n"

        runner = FunctionRunner("test")
        runner.setSubmission(compile(program, "test_code", "exec"))

        runnableSubmission = RunnableStudentSubmission([], runner, ".", 1)
        runnableSubmission.run()

        if runnableSubmission.getException() is not None:
            raise AssertionError(runnableSubmission.getException())


        actualOutput = runnableSubmission.getOutputData()[PossibleResults.RETURN_VAL]

        self.assertEqual(4, actualOutput)
        


        


