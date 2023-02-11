#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: ./util/create_new_autograder.sh <autograder_name> <remote_name>"
    exit 64
fi

if [ ! -d ".git" ]
then
    echo "This script must be run in the root of the autograder repository"
    exit 2
fi

git fetch --all

# Taken from https://git.kernel.org/pub/scm/git/git.git/tree/contrib/completion/git-completion.bash?id=HEAD

currentBranch="$(git symbolic-ref HEAD 2>/dev/null)" ||
currentBranch="(unnamed branch)"     # detached HEAD

currentBranch=${currentBranch##refs/heads/}

if [ "$currentBranch" != "main" ]
then
    if [ "$(git checkout main > /dev/null 2>&1 )" -ne 0 ]
    then
        echo "Failed to swtich from $currentBranch to main"
        exit 2
    fi
    echo "Switched to main branch"
fi

echo "Generating new autograder with name: $1"

git checkout -b $1

echo "Publishing new branch"

git push $2 $1:$1
