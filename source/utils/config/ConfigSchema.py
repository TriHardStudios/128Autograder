import requests
from schema import And, Optional, Regex, Schema

TAGS_ENDPOINT="https://api.github.com/repos/CSCI128/128Autograder/tags"

def getAvaibleTags():
    headers = {"X-GitHub-Api-Version": "2022-11-28"}

    tags = requests.get(url=TAGS_ENDPOINT, headers=headers).json()
    
    return [el["name"] for el in tags]


tags = getAvaibleTags()

CONFIG_SCHEMA = Schema(
    {
        "asignment_name": And(str, Regex(r"^(\w+-?)+$")),
        "semester": And(str, Regex(r"^(F|S|SUM)\d{2}$")),
        "config": {
            "autograder_version": And(str, lambda x: x in tags),
            "enforce_submission_limit": bool,
            Optional("submission_limit", default=1000): And(int, lambda x: x >= 1),
            Optional("take_highest", default=True): bool,
            Optional("allow_extra_credit", default=False): bool,
            "perfect_score": And(int, lambda x: x >= 1),
            "max_score": And(int, lambda x: x >= 1),
            Optional("python", default=dict): {
                Optional("extra_packages", default=list): [{
                    "name": str,
                    "version": str,
                }],
            },
        },
        "build": {
            "use_starter_code": bool,
            "use_data_files": bool,
            Optional("allow_private", default=True): bool,

        }
    })

