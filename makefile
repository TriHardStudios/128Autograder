NAME=128_autograder
ROOT=$(shell pwd)
SHELL=/bin/bash
CLEAN = clean

SUBMISSION_DIR=$(ROOT)/student/submission
RESULTS_DIR=$(ROOT)/student/results

SRC_DIR=$(ROOT)/source
UTIL_DIR=$(SRC_DIR)/utils

all: 
	@echo "Usage make <target>"
	@echo "Available targets:"
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

build-docker: 
	docker build -t $(NAME) $(ROOT)

run-interactive: build-docker
	docker run --rm -it -v $(SUBMISSION_DIR):/autograder/submission -v $(RESULTS_DIR):/autograder/results $(NAME) bash

run: build-docker
	docker run --rm -v $(SUBMISSION_DIR):/autograder/submission -v $(RESULTS_DIR):/autograder/results $(NAME) /autograder/run_autograder && cat $(RESULTS_DIR)/results.json

build:
	@echo "REMOVED: Use python run.py --build --source source -o ../bin"
