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
import ast
import os
import sys
from typing import *
import re
from importlib.util import find_spec


class StudentSubmission:
    @staticmethod
    def _generateImportList(_programAST: ast.Module, _currentlyImportedFiles: Set[str]) -> Set[str]:
        """
        This file generates the list of imports that the student used
        :param _programAST: The AST of the program currently being processed
        :param _currentlyImportedFiles: The list of imported files
        :returns A list of the new imported files
        """
        newImportedFiles: Set[str] = set()

        for node in ast.walk(_programAST):
            if not isinstance(node, ast.Import) and not isinstance(node, ast.ImportFrom):
                continue

            importName: str = node.names[0].name if isinstance(node, ast.Import) else node.module

            # If the module we are currently looking is importable, then we know that it is either an
            #  installed library or and Python standard library and no extra handling is needed
            if find_spec(importName) is not None:
                continue

            fileName = importName.replace('.', '/') + ".py"

            if fileName not in _currentlyImportedFiles:
                newImportedFiles.add(fileName)

        return newImportedFiles

    @staticmethod
    def _generateDisallowedFunctionCalls(_disallowedFunctionSignatures: list[str]) -> list[ast.Call]:
        """
        @brief This function processes a list of strings and converts them into AST function calls.
        It will discard any mismatches.

        @param _disallowedFunctionSignatures: The list of functions calls to convert to AST function calls

        @returns A list of AST function calls
        """

        astCalls: list[ast.Call] = []

        for signature in _disallowedFunctionSignatures:
            try:
                expr: ast.expr = ast.parse(signature, mode="eval").body
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
    def _checkForInvalidFunctionCalls(_parsedPythonProgram: ast.Module, _disallowedFunctions: list[ast.Call]) -> \
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
            if type(node) is not ast.Call:
                continue
            # For now we are ignoring imported functions TODO: fix this
            if type(node.func) is ast.Attribute:
                continue
            for functionCall in _disallowedFunctions:
                # If we are blanket flagging the use of a function ie: flagging all uses of eval
                if node.func.id == functionCall.func.id and len(functionCall.args) == 0:
                    if functionCall.func.id not in invalidCalls.keys():
                        invalidCalls[functionCall.func.id] = 0

                    invalidCalls[functionCall.func.id] += 1
                    continue

                # If the function signature matches. Python is dynamically typed and types are evaluated while its
                #  running rather than at parse time. So just seeing if the id and number of arguments matches.
                #  This is also ignore star arguments.
                if node.func.id == functionCall.func.id and len(node.args) == len(functionCall.args):
                    # Using guilty til proven innocent approach
                    isInvalidCall = True
                    for i, arg in enumerate(functionCall.args):
                        # If the type in an in the argument is a variable and its an exclusive wild card (`_`) then
                        #  we dont care about whats there so skip
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
    def _validateStudentSubmission(_studentMainModule: ast.Module, _disallowedFunctions: list[ast.Call]) -> (
            bool, str):

        # validating function calls
        invalidCalls: dict[str, int] = StudentSubmission._checkForInvalidFunctionCalls(_studentMainModule,
                                                                                       _disallowedFunctions)

        # need to roll import statements
        if not invalidCalls:
            return True, ""

        stringedCalls: str = ""
        for key, value in invalidCalls.items():
            stringedCalls += f"{key}: called {value} times\n"

        # TODO need to expand this to include the number of invalid calls
        return False, f"Invalid Function Calls\n{stringedCalls}"

    def __init__(self, _submissionDirectory: str, _disallowedFunctionSignatures: List[str] | None):
        self.testFiles: List[str] = []
        self.pythonFiles: List[str] = []
        self.requirementsFile: str = ""
        self.studentProgram: Dict[str, ast.Module] = {}
        self.errors: str = ""
        self.importedFiles: Set[str] = set()
        self.submissionDirectory: str = _submissionDirectory

        self._discoverAvailableFiles(_submissionDirectory)
        mainProgramFile: str = self._discoverMainModule(_submissionDirectory)
        self._loadProgram(_submissionDirectory, mainProgramFile, self.importedFiles, programAlais="main")

        self.isValid: bool = len(self.studentProgram) > 0

        self.disallowedFunctionCalls: List[ast.Call] = \
            StudentSubmission._generateDisallowedFunctionCalls(_disallowedFunctionSignatures) \
                if _disallowedFunctionSignatures else []

    def addError(self, _errorName: str, _errorText: str):
        if not _errorName:
            _errorName = "Error"

        if not _errorText:
            return
        self.errors += f"{_errorName}: {_errorText}\n"

    def addValidationError(self, _error: str):
        self.addError("Validation Error", _error)

    def _discoverAvailableFiles(self, _submissionDirectory: str) -> None:
        """
        This function locates the available files in the student's submission.

        It is able to detect
        - test files: ``$^test\w*\.py$``
        - python code files: ``^\w+\.py$``
        - requirements files: ``^requirements\.txt$``

        :param _submissionDirectory: the directory to run discovery in
        """
        if not (os.path.exists(_submissionDirectory) and not os.path.isfile(_submissionDirectory)):
            self.addValidationError("Invalid student submission path")
            return

        testFileRegex: Pattern = re.compile(r"^test\w*\.py$")
        requirementsFileRegex: Pattern = re.compile(r"^requirements.txt$")
        pythonFileRegex: Pattern = re.compile(r"^\w+\.py$")

        # TODO: implement ability to traverse sub folders
        for file in os.listdir(_submissionDirectory):
            if not os.path.isfile(os.path.join(_submissionDirectory, file)):
                continue

            if re.match(testFileRegex, file):
                self.testFiles.append(file)
                continue

            if re.match(pythonFileRegex, file):
                self.pythonFiles.append(file)
                continue

            if re.match(requirementsFileRegex, file):
                self.requirementsFile = file
                continue

    def _discoverMainModule(self, _submissionDirectory: str) -> str:
        """
        @brief This function locates the main module
        """
        mainProgramFile: str = ""
        if len(self.pythonFiles) == 0:
            self.addValidationError("No .py files were found")
            return ""

        if len(self.pythonFiles) == 1:
            mainProgramFile = self.pythonFiles[0]
        else:
            # If using multiple files, must have one called main.py
            filteredFiles: List[str] = [file for file in self.pythonFiles if file == "main.py"]
            if len(filteredFiles) == 1:
                mainProgramFile = filteredFiles[0]

        if not mainProgramFile:
            self.addValidationError("Unable to find main file")

        return mainProgramFile

    def _loadProgram(self, _submissionDirectory: str, _programFileName: str, _importList: Set[str],
                     programAlais: str = None):
        fileToOpen: os.path = os.path.join(_submissionDirectory, _programFileName)
        try:
            with open(fileToOpen, 'r') as r:
                programText = r.read()

        except Exception as exG:
            self.addError("IO Error", type(exG).__qualname__)
            return

        try:
            if programAlais is not None:
                _programFileName = programAlais
            self.studentProgram[_programFileName] = ast.parse(programText)
        except SyntaxError as exSe:
            self.addError("Syntax Error", f"{fileToOpen}:{exSe.lineno}: {exSe.msg}: {exSe.text}")
            return

        newImportedFiles: Set[str] = \
            self._generateImportList(self.studentProgram[_programFileName], _importList)

        _importList.update(newImportedFiles)

        for file in newImportedFiles:
            self._loadProgram(_submissionDirectory, file, _importList)

        self.importedFiles = _importList

    def installRequirements(self):
        if not self.requirementsFile:
            return

        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                               '-r', f'{os.path.join(self.submissionDirectory, self.requirementsFile)}'])

    def removeRequirements(self):
        if not self.requirementsFile:
            return

        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall',
                               '-r', f'{os.path.join(self.submissionDirectory, self.requirementsFile)}', '-y'])

    def validateSubmission(self):
        # If we already ran into a validation error when loading submission

        if not self.isValid:
            return

        for file in self.studentProgram.values():
            validationTuple: (bool, str) = \
                StudentSubmission._validateStudentSubmission(file, self.disallowedFunctionCalls)

            self.isValid = self.isValid & validationTuple[0]
            self.addValidationError(validationTuple[1])

    def isSubmissionValid(self) -> bool:
        return self.isValid

    def getValidationError(self) -> str:
        return self.errors

    def getImports(self):
        return dict(zip(
            [f"{os.path.join(self.submissionDirectory, file)}" for file in self.importedFiles],
            [file for file in self.importedFiles]
        ))

    def getTestFiles(self):
        return [f"{os.path.join(self.submissionDirectory, file)}" for file in self.testFiles]

    def getStudentSubmissionCode(self):
        return compile(self.studentProgram["main"], "student_submission", "exec")
