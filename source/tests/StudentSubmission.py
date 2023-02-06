"""
This class exposes a student submission to a test suite.
It helps facitate the reading of a submission, the standard i/o of a submission,
and the running of functions and classes with in a submission.

MUST SUPPORT:
-   tracing AST for disallowed functions
-   providing an interface for calling functions
-   provide an interface for calling classes
-   standard i/o mocking
-   discovering student submissions
-   supporting multiple files

"""
import os
import ast
from io import StringIO
import sys
import signal


class StudentSubmission:
    def __init__(self, _submissionDirectory: str, _disallowedFunctionSignatures: list[str] | None):
        mainModuleTuple = StudentSubmission.__discoverMainModule__(_submissionDirectory)
        self.studentMainModule: ast.Module = mainModuleTuple[0]
        self.validationError: str = mainModuleTuple[1]
        self.isValid: bool = True if self.studentMainModule else False

        self.disallowedFunctionCalls: list[ast.Call] = \
            StudentSubmission.__generateDisallowedFunctionCalls__(_disallowedFunctionSignatures) \
                if _disallowedFunctionSignatures else []

    @staticmethod
    def __discoverMainModule__(_submissionDirectory: str) -> (ast.Module, str):
        """
        @brief This function locates the main module
        """
        if not (os.path.exists(_submissionDirectory) and not os.path.isfile(_submissionDirectory)):
            return None, "Validation Error: Invalid student submission path"

        fileNames: list[str] = [file for file in os.listdir(_submissionDirectory) if file[-3:] == ".py"]

        if len(fileNames) == 0:
            return None, "Validation Error: No .py files were found"
        fileName: str = ""

        if len(fileNames) == 1:
            fileName = _submissionDirectory + fileNames[0]
        else:
            # If using multiple files, must have one called main.py
            filteredFiles: list[str] = [file for file in fileNames if fileName == "main.py"]
            if len(filteredFiles) == 1:
                fileName = filteredFiles[0]
        if not fileName:
            return None, "Validation Error: Unable to find main file"

        pythonProgramText: str = None

        try:
            pythonProgramText = open(fileName, 'r').read()
        except Exception as ex_g:
            return None, f"IO Error: {ex_g.msg}"


        parsedPythonProgram: ast.Module = None

        try:
            parsedPythonProgram = ast.parse(pythonProgramText)

        except SyntaxError as ex_se:
            return None, f"Syntax Error: {ex_se.msg} on line {ex_se.lineno}"

        return parsedPythonProgram, ""

    @staticmethod
    def __generateDisallowedFunctionCalls__(_disallowedFunctionSignatures: list[str]) -> list[ast.Call]:
        """
        @brief This function processes a list of strings and converts them into AST function calls.
        It will discard any mismatches.

        @param _disallowedFunctionSignatures: The list of functions calls to convert to AST function calls

        @returns A list of AST function calls
        """

        astCalls: list[ast.Call] = []

        for signature in _disallowedFunctionSignatures:
            try:
                expr: ast.Expr = ast.parse(signature, mode="eval").body
                if not isinstance(expr, ast.Call):
                    print(
                        f"Failed to parse function signature: {signature}. Incorrect type: Parsed type is {type(expr)}")
                    continue
                astCalls.append(expr)
            except SyntaxError as ex_se:
                print(f"Failed to parse function signature: {signature}. Syntax error: {ex_se.msg}")
                continue

        return astCalls

    @staticmethod
    def __checkForInvalidFunctionCalls__(_parsedPythonProgram: ast.Module, _disallowedFunctions: list[ast.Call]) -> \
    dict[str, int]:
        """
        @brief This function checks to see if any of the functions that a student used are on a 'black list' of disallowedFunctions.
        This function works by taking a parsed python script and walks the AST to see if any of the called functions are disallowed.

        @param _parsedPythonProgram: The parsed python module. Must be an AST module (ast.Module)
        @param _disallowedFunctions: The function 'black list'. But be a list of AST functions calls (ast.Call)

        @returns A dictionary containing the number of times each disallowed function was called
        """

        # validating function calls
        invalidCalls: dict[str, int] = {}
        # This walks through every node in the program and sees if it is invalid
        for node in ast.walk(_parsedPythonProgram):
            if type(node) is ast.Call:
                for functionCall in _disallowedFunctions:
                    # If we are blanket flagging the use of a function ie: flagging all uses of eval
                    if node.func.id == functionCall.func.id and len(functionCall.args) == 0:
                        if functionCall.func.id not in invalidCalls.keys():
                            invalidCalls[functionCall.func.id] = 0

                        invalidCalls[functionCall.func.id] += 1
                        continue

                    # If the function sigiture matches. Python is dynamically typed and types are evaluated while its running rather than at
                    #  parse time. So just seeing if the id and number of arguments matches. This is also ignore star arugments.
                    if node.func.id == functionCall.func.id and len(node.args) == len(functionCall.args):
                        # Using guilty til proven innocent approach
                        isInvalidCall = True
                        for i, arg in enumerate(functionCall.args):
                            # If the type in a in the arugment is a variable and its a exclusive wild card (`_`) then we dont care about whats there so skip
                            if type(arg) is ast.Name and arg.id == '_':
                                continue

                            # If there is a constant where there is a variable - then its a mismatch
                            if type(arg) is ast.Name and type(node.args[i]) is not ast.Name:
                                isInvalidCall = False
                                break

                            # If the constant values don't match - then its a mismatch
                            if (type(arg) is ast.Constant and type(node.args[i]) is ast.Constant) and arg.value is not \
                                    node.args[i].value:
                                isInvalidCall = False
                                break

                        if isInvalidCall:
                            if functionCall.func.id not in invalidCalls.keys():
                                invalidCalls[functionCall.func.id] = 0

                            invalidCalls[functionCall.func.id] += 1

        return invalidCalls

    @staticmethod
    def __validateStudentSubmission__(_studentMainModule: ast.Module, _disallowedFunctions: list[ast.Call]) -> (bool, str):
        # validating function calls
        invalidCalls: dict[str, int] = StudentSubmission.__checkForInvalidFunctionCalls__(_studentMainModule,
                                                                                          _disallowedFunctions)

        if not invalidCalls:
            return True, ""

        stringedCalls: str = ""
        for key, value in invalidCalls.items():
            stringedCalls += f"{key}: called {value} times\n"

        # TODO need to expand this to include the number of invalid calls
        return False, f"Invalid Function Calls\n{stringedCalls}"

    def validateSubmission(self):
        # If we already ran into a validation error when loading submission

        if not self.isValid:
            return

        validationTuple: (bool, str) = StudentSubmission.__validateStudentSubmission__(self.studentMainModule,
                                                                                       self.disallowedFunctionCalls)

        self.isValid = validationTuple[0]
        self.validationError = validationTuple[1]

    def isSubmissionValid(self) -> bool:
        return self.isValid

    def isSubmissionAModule(self) -> bool:
        return self.isModule

    def getValidationError(self) -> str:
        return self.validationError

    @staticmethod
    def __execWrapper__(_compiledPythonProgram, _timeout: int):
        class TimeoutError(Exception):
            pass

        def catchTimeout():
            raise TimeoutError()

        signal.signal(signal.SIGTERM, catchTimeout)
        signal.alarm(_timeout)

        try:
            exec(_compiledPythonProgram)
        except TimeoutError:
            pass
        finally:
            signal.alarm(0)


    def runMainModule(self, _stdIn: list[str], timeoutDuration: int = 10) -> (bool, list[str]):
        """
        @brief This function compiles and runs python code from the AST
        """
        if not self.isValid:
            return False, []

        try:
            compiledPythonProgram = compile(self.studentMainModule, "<student_submission>", "exec")
            # This can also cause a stack overflow - but lets not worry about that
        except (SyntaxError, ValueError) as g_ex:
            return False, [g_ex]

        oldStdOut = sys.stdout
        oldStdIn = sys.stdin

        stdIn = sys.stdin = StringIO("".join([line + "\n" for line in _stdIn]))
        capturedOutput = sys.stdout = StringIO()
        stdOut: list[str] = []

        try:
            StudentSubmission.__execWrapper__(compiledPythonProgram, timeoutDuration)
            capturedOutput.seek(0)
            stdOut = capturedOutput.getvalue().splitlines()
        except Exception as g_ex:
            sys.stdin = oldStdIn
            sys.stdout = oldStdOut
            return False, [f"A runtime occured. Exception type is {type(g_ex).__qualname__}"]

        sys.stdin = oldStdIn
        sys.stdout = oldStdOut
        stdOut = StudentSubmission.filterStdOut(stdOut)
        return True, stdOut

    @staticmethod
    def filterStdOut(_stdOut: list[str]) -> list[str]:
        """
        @breif This function takes in a list representing the output from the program. It includes ALL output,
        so lines may appear as 'NUMBER> OUTPUT 3' where we only care about what is right after the OUTPUT statement
        This is adapted from John Henke's implmentation
        """

        filteredOutput: list[str] = []
        for line in _stdOut:
            if "output " in line.lower():
                filteredOutput.append(line[line.lower().find("output ") + 7:])

        return filteredOutput


