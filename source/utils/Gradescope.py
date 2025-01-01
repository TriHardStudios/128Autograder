from typing import Dict
import json
import os
from lib.config import AutograderConfiguration


def gradescopePostProcessing(autograderResults: Dict, autograderConfiguration: AutograderConfiguration, metadataPath: str):
    if not os.path.exists(metadataPath):
        return

    # for now, we aren't implementing any new features for this
    submissionLimit = autograderConfiguration.config.submission_limit
    takeHighest = autograderConfiguration.config.take_highest

    # Enforce submission limit
    submissionMetadata: dict = {}
    with open(metadataPath, 'r') as submissionMetadataIn:
        submissionMetadata = json.load(submissionMetadataIn)

    previousSubmissions: list[dict] = submissionMetadata['previous_submissions']

    autograderResults['output'] = f"Submission {len(previousSubmissions) + 1} of {submissionLimit}.\n"

    validSubmissions: list[dict] = \
        [previousSubmissionMetadata['results']
         for previousSubmissionMetadata in previousSubmissions
         if 'results' in previousSubmissionMetadata.keys()
         ]

    validSubmissions.append(autograderResults)

    # submission limit exceeded
    if len(validSubmissions) > submissionLimit:
        autograderResults['output'] += f"Submission limit exceeded.\n" \
                              f"Autograder has been run on your code so you can see how you did\n" \
                              f"but, your score will be highest of your valid submissions.\n"
        validSubmissions = validSubmissions[:submissionLimit]
        # We should take the highest valid submission
        takeHighest = True

    # sorts in descending order
    validSubmissions.sort(reverse=True, key=lambda submission: submission['score'] if 'score' in submission else 0)

    if takeHighest and validSubmissions[0] != autograderResults:
        autograderResults['output'] += f"Score has been set to your highest valid score.\n"
        autograderResults['score'] = validSubmissions[0]['score']

    # ensure that negative scores arent possible
    if autograderResults['score'] < 0:
        autograderResults['output'] += f"Score has been set to a floor of 0 to ensure no negative scores.\n"
        autograderResults['score'] = 0
