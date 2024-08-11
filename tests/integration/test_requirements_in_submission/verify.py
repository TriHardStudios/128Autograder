import json
import os

assert os.path.exists("results/results.json")

with open("results/results.json") as r:
    results = json.load(r)

assert results['score'] == 10

assert "<figure>" in results["tests"][0]["output"]