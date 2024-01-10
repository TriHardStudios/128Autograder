#!/bin/bash


rm -rf bin/*

python source/run.py --config-file ./config.toml --build --source source -o ./bin
