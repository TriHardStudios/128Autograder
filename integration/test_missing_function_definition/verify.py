import json
import os

assert os.path.exists("results/results.json")

with open("results/results.json") as r:
    results = json.load(r)

testResult = results['tests'][0]

assert results['score'] == 0

assert "missing the function definition" in testResult['output']
# THIS NEEDS TO BE FIXED
# assert testResult['output'].count("missing the function definition") == 1
