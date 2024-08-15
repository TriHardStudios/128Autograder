import os

assert os.path.exists("./bin/generation/student/")
assert os.path.exists("./bin/generation/gradescope/")

gradescopeExpectedTestFiles = [file for file in os.listdir("./student_tests/") if os.path.isfile(os.path.join("student_tests", file))]
gradescopeExpectedTestFiles.sort()

studentExpectedFiles = [file for file in gradescopeExpectedTestFiles if "test_public" in file]
studentExpectedFiles.sort()

gradescopeActualTestFiles = [file for file in os.listdir("./bin/generation/gradescope/student_tests/") if os.path.isfile(os.path.join("./bin/generation/gradescope/student_tests/", file))]
gradescopeActualTestFiles.sort()

studentActualFiles = [file for file in os.listdir("./bin/generation/student/student_tests/") if os.path.isfile(os.path.join("./bin/generation/student/student_tests/", file))]
studentActualFiles.sort()


assert gradescopeExpectedTestFiles == gradescopeActualTestFiles
assert studentExpectedFiles == studentActualFiles

expectedStarterCode = os.listdir("./starter_code/")

actualStarterCode = os.listdir("./bin/generation/student/student_work/")
actualStarterCode = [file for file in actualStarterCode if file[-3:] == ".py"]

assert len(actualStarterCode) == 1
assert expectedStarterCode == actualStarterCode

# assert that it did not get pulled in to gradescope
assert not os.path.exists("./bin/generation/gradescope/starter_code/")


expected_public = os.listdir("./student_tests/data/files/test_public/")
expected_public.sort()

expected_private = os.listdir("./student_tests/data/files/test_private/")
expected_private.sort()

gradescope_expected_directories = ["test_public", "test_private"]
gradescope_expected_directories.sort()

student_expected_directories = ["test_public"]

gradescope_actual_directories = os.listdir("./bin/generation/gradescope/student_tests/data/files/")
gradescope_actual_directories.sort()

student_actual_directories = os.listdir("./bin/generation/student/student_tests/data/files/")

assert gradescope_expected_directories == gradescope_actual_directories
assert student_expected_directories == student_actual_directories

student_actual_files_data_folder = os.listdir("./bin/generation/student/student_tests/data/files/test_public/")
student_actual_files_data_folder.sort()

assert expected_public == student_actual_files_data_folder

student_student_work_folder = os.listdir("./bin/generation/student/student_work/")

for file in expected_public:
    assert file in student_student_work_folder

for file in expected_private:
    assert file not in student_student_work_folder


gradescope_actual_public_files = os.listdir("./bin/generation/gradescope/student_tests/data/files/test_public")
gradescope_actual_public_files.sort()

gradescope_actual_private_files = os.listdir("./bin/generation/gradescope/student_tests/data/files/test_private")
gradescope_actual_private_files.sort()

assert gradescope_actual_private_files == expected_private
assert gradescope_actual_public_files == expected_public

