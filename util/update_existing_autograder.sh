#!/bin/bash

if [ $# -ne 1 ]
then
  echo "Usage: ./update_existing_autograder.sh <autograder_name>"
  exit 64
fi

if [ ! -d ".git" ]
then
    echo "This script must be run in the root of the autograder repository"
    exit 2
fi

if [ ! -d "autograder_base" ]
then
  echo "Autograder base not found. Please ensure that you cloned all submodules"
  exit 2
fi

if [ ! -d "$1" ]
then
  echo "No autograder found in ./$1 Please run ./create_new_autograder.sh"
  exit 2
fi

pushd autograder_base > /dev/null
git pull
popd > /dev/null

echo "Updating autograder version for autograder in /$1..."

# Copy over submission api
cp -r autograder_base/source/StudentSubmission "$1"/source/

# Copy over main
cp autograder_base/source/run.py "$1"/source/run.py

# Copy over requirements
cp autograder_base/source/requirements.txt "$1"/source/requirements.txt

cp autograder_base/{Dockerfile,makefile} "$1"/

# Copy over student utils
cp -r autograder_base/util/student "$1"/util/

# copy over generation utils
cp autograder_base/util/{prepare_for_student.sh,prepare_for_gradescope.sh} "$1"/util/

git add "$1"
git commit -m "[UPDATE] Bump autograder version for autograder $1 in ./$1"
git push


