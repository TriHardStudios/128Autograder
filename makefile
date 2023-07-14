NAME=128_autograder
ROOT=$(shell pwd)
SHELL=/bin/bash

SUBMISSION_DIR=$(ROOT)/student/submission
RESULTS_DIR=$(ROOT)/student/results

SRC_DIR=$(ROOT)/source
UTIL_DIR=$(ROOT)/util

BUILD_DIR=$(ROOT)/bin
GENERATION_DIR=$(BUILD_DIR)/generation
GRADESCOPE_GENERATION_DIR=$(GENERATION_DIR)/gradescope
STUDENT_GENERATION_DIR=$(GENERATION_DIR)/student
UPLOAD_DIR=$(BUILD_DIR)/uploaders

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


build: clean
	$(if $(autograder_name),,  \
		@echo "Build MUST be invoked with autograder_name=<name>"; \
		echo "For example: make build autograder_name=F2022-101-Teslacoils"; \
		exit 64; \
	)
	@echo "Preparing autograder: $(autograder_name) for upload..."
	@echo "	Generating autograder source in $(GENERATION_DIR) from $(SRC_DIR)..."
	@mkdir -p $(GRADESCOPE_GENERATION_DIR)
	@mkdir -p $(STUDENT_GENERATION_DIR)
	@bash util/prepare_for_gradescope.sh $(GRADESCOPE_GENERATION_DIR) $(SRC_DIR)
	@bash util/prepare_for_student.sh $(STUDENT_GENERATION_DIR) $(UTIL_DIR) $(SRC_DIR)
	@echo "	Building Gradescope autograder in $(UPLOAD_DIR)/$(autograder_name).zip..."
	@mkdir -p $(UPLOAD_DIR)
	@echo "		Creating zip..."
	@pushd $(GRADESCOPE_GENERATION_DIR) > /dev/null ; zip -r $(autograder_name) . -x .* > /dev/null ; popd > /dev/null 
	@echo "		Moving zip to output directory..."
	@mv $(GRADESCOPE_GENERATION_DIR)/$(autograder_name).zip $(UPLOAD_DIR)/$(autograder_name).zip
	@echo "	Building student autograder in $(UPLOAD_DIR)/$(autograder_name)-student.zip..."
	@echo "		Creating student zip..."
	@pushd $(STUDENT_GENERATION_DIR) > /dev/null ; zip -r $(autograder_name) . -x .* > /dev/null ; popd > /dev/null 
	@echo "		Moving zip to output directory..."
	@mv $(STUDENT_GENERATION_DIR)/$(autograder_name).zip $(UPLOAD_DIR)/$(autograder_name)-student.zip
	@echo "Done."

clean: 
	@if [ -d "$(BUILD_DIR)" ]; then \
		echo "Cleaning up autograders..."; \
		rm -r $(BUILD_DIR); \
	fi

