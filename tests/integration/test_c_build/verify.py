import json
import os

assert os.path.exists("results/results.json")

with open("results/results.json") as r:
    results = json.load(r)

# TODO - Update this once we fix the issues with the c runner
assert results['score'] == 0
