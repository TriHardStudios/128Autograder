#!/bin/bash


rm -rf bin/*

make CLEAN= build autograder_name=test_build
