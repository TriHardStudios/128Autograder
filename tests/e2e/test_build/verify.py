import os

assert os.path.exists("./bin/generation/student/")
assert os.path.exists("./bin/generation/docker/gradescope/")

expected_source_directories = ["Executors", "StudentSubmission", "StudentSubmissionImpl", "Tasks", "TestingFramework"]

actual_gs_dirs = os.listdir("./bin/generation/docker/gradescope/")
actual_student_dirs = os.listdir("./bin/generation/student/")

for file in expected_source_directories:
    assert file in actual_gs_dirs
    assert file in actual_student_dirs

dockerExpectedTestFiles = [file for file in os.listdir("./student_tests/") if os.path.isfile(os.path.join("student_tests", file))]
dockerExpectedTestFiles.sort()

studentExpectedFiles = [file for file in dockerExpectedTestFiles if "test_public" in file]
studentExpectedFiles.sort()

dockerActualTestFiles = [file for file in os.listdir("./bin/generation/docker/gradescope/student_tests/") if os.path.isfile(os.path.join("./bin/generation/docker/gradescope/student_tests/", file))]
dockerActualTestFiles.sort()

studentActualFiles = [file for file in os.listdir("./bin/generation/student/student_tests/") if os.path.isfile(os.path.join("./bin/generation/student/student_tests/", file))]
studentActualFiles.sort()


assert dockerExpectedTestFiles == dockerActualTestFiles
assert studentExpectedFiles == studentActualFiles

expectedStarterCode = os.listdir("./starter_code/")

actualStarterCode = os.listdir("./bin/generation/student/student_work/")
actualStarterCode = [file for file in actualStarterCode if file[-3:] == ".py"]

assert len(actualStarterCode) == 1
assert expectedStarterCode == actualStarterCode

# assert that it did not get pulled in to docker
assert not os.path.exists("./bin/generation/docker/gradescope/starter_code/")


expected_public = os.listdir("./student_tests/data/files/test_public/")
expected_public.sort()

expected_private = os.listdir("./student_tests/data/files/test_private/")
expected_private.sort()

docker_expected_directories = ["test_public", "test_private"]
docker_expected_directories.sort()

student_expected_directories = ["test_public"]

docker_actual_directories = os.listdir("./bin/generation/docker/gradescope/student_tests/data/files/")
docker_actual_directories.sort()

student_actual_directories = os.listdir("./bin/generation/student/student_tests/data/files/")

assert docker_expected_directories == docker_actual_directories
assert student_expected_directories == student_actual_directories

student_actual_files_data_folder = os.listdir("./bin/generation/student/student_tests/data/files/test_public/")
student_actual_files_data_folder.sort()

assert expected_public == student_actual_files_data_folder

student_student_work_folder = os.listdir("./bin/generation/student/student_work/")

for file in expected_public:
    assert file in student_student_work_folder

for file in expected_private:
    assert file not in student_student_work_folder


docker_actual_public_files = os.listdir("./bin/generation/docker/gradescope/student_tests/data/files/test_public")
docker_actual_public_files.sort()

docker_actual_private_files = os.listdir("./bin/generation/docker/gradescope/student_tests/data/files/test_private")
docker_actual_private_files.sort()

assert docker_actual_private_files == expected_private
assert docker_actual_public_files == expected_public

