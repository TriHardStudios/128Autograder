#!/bin/sh

cd /app/source/utils/student || exit 1

python /app/source/utils/student/test_my_work.py /app/submission > /app/results/output.txt
