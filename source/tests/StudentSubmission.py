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


class StudentSubmission:
    def __init__(self, _submissionDirectory: str, _disallowedFunctionSignatures: list[str] | None):
        self.validationError = None
        mainModuleTuple: (str, any) = StudentSubmission.__discoverMainModule__(_submissionDirectory)
        self.mainModulePath: str = mainModuleTuple[0]
        self.mainModule: any = mainModuleTuple[1]
        self.isModule: bool = self.mainModule is not None
        self.isValid: bool = False

        self.disallowedFunctionCalls: list[ast.Call] = \
            StudentSubmission.__generateDisallowedFunctionCalls__(
                _disallowedFunctionSignatures) if _disallowedFunctionSignatures else []

    @staticmethod
    def __discoverMainModule__(_submissionDirectory: str) -> (str, any):
        """
        @brief This function attempts to locate the students submision and determines how to process it based on the syntax
        """
        if not (os.path.exists(_submissionDirectory) and not os.path.isfile(_submissionDirectory)):
            raise Exception("Invalid Path")

        files: list[str] = [file for file in os.listdir(_submissionDirectory) if file[-3:] == ".py"]

        if len(files) == 0:
            raise Exception("No '.py' files found")
        file: str = ""

        if len(files) == 1:
            file = _submissionDirectory + files[0]
        else:
            # If using multiple files, must have one called main.py
            filteredFiles: list[str] = [file for file in files if file == "main.py"]
            if len(filteredFiles) == 1:
                file = filteredFiles[0]
        if not file:
            raise Exception("Unable to find main file")

        isModule: bool = False  # This will be set to true if its possible to import this program

        # This is prolly not the best way to do this
        #  Basically the way that I'm checking to see if this is a module is by seeing if it has the module protection if statment
        #  (thats prolly not the right word but alas)
        # TODO Need to integrate with AST parsing. But also want to avoid double parsing prolly
        with open(file, 'r') as pythonProgram:
            if "if __name__ == \"__main__\":" in pythonProgram:
                isModule = True

        # If we try to import a non module then it will run the code and cause this process to hang
        if isModule:
            # TODO add some protection against running any code in a potentionally ill formed file
            return file, __import__(file.replace("/", "."))

        return file, None

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
    def __validateStudentSubmission__(_mainModulePath: str, _disallowedFunctions: list[ast.Call]) -> (bool, str):
        # the file should exits if we got here so not needed to validate

        pythonProgram: str = open(_mainModulePath, 'r').read();
        parsedPythonProgram: ast.Module | None = None

        # in the event of a syntax error - this will throw an expection
        try:
            parsedPythonProgram = ast.parse(pythonProgram)

        except SyntaxError as ex_se:
            print(f"Syntax Error: {ex_se.msg}")
            return False, ex_se.msg

        print("Validating student submission...")

        # validating function calls
        invalidCalls: dict[str, int] = StudentSubmission.__checkForInvalidFunctionCalls__(parsedPythonProgram,
                                                                                          _disallowedFunctions)

        if not invalidCalls:
            return True, ""

        print(invalidCalls)
        stringedCalls: str = ""
        for key, value in invalidCalls.items():
            stringedCalls += f"{key}: called {value} times\n"

        # TODO need to expand this to include the number of invalid calls
        return False, f"Invalid Function Calls\n{stringedCalls}"

    def validateSubmission(self):
        validationTuple: (bool, str) = StudentSubmission.__validateStudentSubmission__(self.mainModulePath,
                                                                                       self.disallowedFunctionCalls)

        self.isValid = validationTuple[0]
        self.validationError = validationTuple[1]
        if not self.isValid:
            print(f"Submission is invalid. Reason: {validationTuple[1]}")

    def isSubmissionValid(self) -> bool:
        return self.isValid

    def isSubmissionAModule(self) -> bool:
        return self.isModule

    def getValidationError(self) -> str:
        return self.validationError

    def runModule(self, _stdIn: list[str]) -> (bool, list[str]):
        """
        @brief This function compiles and runs python code from the AST
        """
        if not self.isValid:
            return False, []

        pythonProgram = open(self.mainModulePath, 'r').read()

        try:
            parsedPythonProgram: ast.Module = ast.parse(pythonProgram)
        except SyntaxError:
            return False, []

        try:
            compiledPythonProgram: code = compile(parsedPythonProgram, "<student_submission>", "exec")
            # This can also cause a stack overflow - but lets not worry about that
        except (SyntaxError, ValueError):
            return False, []

        oldStdOut = sys.stdout
        oldStdIn = sys.stdin

        stdIn = sys.stdin = StringIO("".join([line + "\n" for line in _stdIn]))
        capturedOutput = sys.stdout = StringIO()
        stdOut: list[str] = []

        try:
            exec(compiledPythonProgram)
            capturedOutput.seek(0)
            stdOut = capturedOutput.getvalue().splitlines()
        except Exception:
            sys.stdin = oldStdIn
            sys.stdout = oldStdOut
            return False, []

        sys.stdin = oldStdIn
        sys.stdout = oldStdOut
        stdOut = StudentSubmission.filterStdOut(stdOut)
        # print("".join(["OUTPUT " + line + "\n" for line in stdOut]))
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
