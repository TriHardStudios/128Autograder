NAME=autograder_prototype
ROOT=$(shell pwd)
SHELL=/bin/bash

SUBMISSION_DIR=$(ROOT)/student/submission
RESULTS_DIR=$(ROOT)/student/results

SRC_DIR=$(ROOT)/source

BUILD_DIR=$(ROOT)/bin
GENERATION_DIR=$(BUILD_DIR)/gradescope_generation
UPLOAD_DIR=$(BUILD_DIR)/gradescope_upload

all: 
	@echo "Usage make <target>"
	@echo "Avaible targets:"
	# I stole this from stackoverflow - it prints out all the targets in a makefile
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)(\n|$$)/,/(^|\n) / {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

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
	@mkdir -p $(GENERATION_DIR)
	@bash util/prepare_for_gradescope.sh $(GENERATION_DIR) $(SRC_DIR)
	@echo "	Building autograder in $(UPLOAD_DIR)/$(autograder_name).zip..."
	@mkdir -p $(UPLOAD_DIR)
	@echo "		Creating zip..."
	@pushd $(GENERATION_DIR) > /dev/null ; zip -r $(autograder_name) . -x .* > /dev/null ; popd > /dev/null 
	@echo "		Moving zip to output directory..."
	@mv $(GENERATION_DIR)/$(autograder_name).zip $(UPLOAD_DIR)/$(autograder_name).zip
	@echo "Done."

clean: 
	@if [ -d "$(BUILD_DIR)" ]; then \
		echo "Cleaning up autograders..."; \
		rm -r $(BUILD_DIR); \
	fi

