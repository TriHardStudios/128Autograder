#!/bin/bash


rm -rf bin/*

cd source

python run.py --build -o ../bin
