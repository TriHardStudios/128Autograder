import json
import os

assert os.path.exists("results/results.json")

with open("results/results.json") as r:
    results = json.load(r)

assert results['score'] == 9.5

assert "4 of" in results['output']
assert "highest valid score" in results['output']
