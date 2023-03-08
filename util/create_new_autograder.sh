#!/bin/bash


if [ $# -ne 1 ]
then
    echo "Usage: ./util/create_new_autograder.sh <autograder_name>"
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

# Update autograder base
pushd autograder_base > /dev/null
git pull
popd > /dev/null

mkdir -p "$1"/source "$1"/student "$1"/util

cp -r autograder_base/source "$1"/source
cp -r autograder_base/student/{results/.gitkeep,submission/.gitkeep} "$1"/student
cp autograder_base/util/prepare_for_gradescope.sh "$1"/source/util/prepare_for_gradescope.sh
cp -r autograder_base/{makefile,Dockerfile,.gitignore} "$1"/
