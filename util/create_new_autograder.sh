#!/bin/bash


if [ $# -ne 1 ]
then
    echo "Usage: ./create_new_autograder.sh <autograder_name>"
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

if [ -d "$1" ]
then
    echo "Autograder found in $1. Please use ./update_autograder.sh"
    exit 2
fi

# Update autograder base
pushd autograder_base > /dev/null
git pull
popd > /dev/null

# Copy over the source files
echo "Generating new autograder in ./$1/ ..."
mkdir -p "$1"/source "$1"/student/submission "$1"/student/results "$1"/util/student

cp -r autograder_base/source "$1"/

# Copy over student utils
cp -r autograder_base/util/student "$1"/util/

# copy over generation utils
cp autograder_base/util/{prepare_for_student.sh,prepare_for_gradescope.sh} "$1"/util/


cp -r autograder_base/{makefile,Dockerfile,.gitignore} "$1"/



git add "$1"
git commit -m "[NEW] Added base autograder for new autograder $1 in ./$1"
git push
