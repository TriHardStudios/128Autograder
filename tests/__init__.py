# This adds the source directory to the os path
# this is stolen verbatim from https://stackoverflow.com/a/59732673
# this is pretty hacky but it works haha
# adding the student scripts

import os
import sys

project_path = os.getcwd()

source_path = os.path.join(project_path, "source")

sys.path.append(source_path)
