import os

assert os.path.exists("./bin/generation/student/")


expectedStarterCode = os.listdir("./studentTests/data/starter_code/")
expectedStarterCode.sort()

actualStarterCode = os.listdir("./bin/generation/student/student_work/")
actualStarterCode.sort()
# ignore any .keep
actualStarterCode = [file for file in actualStarterCode if file != ".keep"]

assert expectedStarterCode == actualStarterCode

# assert that it did not get pulled in to gradescope
assert not os.path.exists("./bin/generation/gradescope/studentTests/data/starter_code/")

