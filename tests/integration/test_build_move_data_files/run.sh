#!/bin/bash


rm -rf bin/*

cd source

python run.py --config-file ../config.toml --build -o ../bin
