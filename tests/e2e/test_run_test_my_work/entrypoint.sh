#!/bin/sh

## build autograder
#
#mkdir -p /app/build
#
#python run.py --build -o /app/build || exit 1
#
## go to student directory
#cd /app/build/generation/student || exit 1

# run the boi in a more realistic way
# we are just overriding the submission diretory to point to the already correct submission
test_my_work --submission-directory /app/submission > /app/results/output.txt
