# must be used as ./prepare_for_student.sh <student_generation_dir> <utilities_dir>  <autograder_source>



find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

# file structure must be
# (root)
# |_test_my_work.py
# |_create_gradescope_upload.py
# |_run.py
# |_requirements.txt
# |
# |_StudentSubmission
# | |_...
# |
# |_TestingFrameWork
# | |_...
# |
# |_studentTests
#   |_test_public_*.py

# Copy over base files.
cp "$3"/run.py "$1"/run.py
cp "$3"/requirements.txt "$1"/requirements.txt

# copy over testing framework
cp -r "$3"/TestingFramework "$1"/TestingFramework
cp -r "$3"/StudentSubmission "$1"/StudentSubmission


mkdir "$1"/studentTests 2> /dev/null

# copy over public tests
# test files are assumed to be private unless they have the format test_public_*.py.
cp "$3"/studentTests/test_public*.py "$1"/studentTests/

# copy over student submission utilities

cp "$2"/student/test_my_work.py "$1"/test_my_work.py
cp "$2"/student/create_gradescope_upload.py "$1"/create_gradescope_upload.py


# create student work folder
mkdir "$1"/student_work
touch "$1"/student_work/.keep

