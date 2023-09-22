import os

assert os.path.exists("./bin/generation/gradescope/")
assert os.path.exists("./bin/generation/student/")

gradescopeExpectedFiles = os.listdir("./studentTests/")
gradescopeExpectedFiles.sort()

studentExpectedFiles = [file for file in gradescopeExpectedFiles if "test_public" in file]
studentExpectedFiles.sort()

gradescopeActualFiles = os.listdir("./bin/generation/gradescope/studentTests/")
gradescopeActualFiles.sort()

studentActualFiles = os.listdir("./bin/generation/student/studentTests/")
studentActualFiles.sort()


assert gradescopeExpectedFiles == gradescopeActualFiles
assert studentExpectedFiles == studentActualFiles

