import json

import ollama

from utils import extract_bracket_content


def resumeEvaluation(job_desc, resume_text, accuracy):
    resume_msg = '''Given below is the resume of candidate'''
    jd_msg = '''This is a Json object containing the job requirements for the role.'''

    prompt_msg = '''Evaluate if the resume of candidate fits each job requirement. Based on relevance rate it as 
    Low/Medium/High. Low for no relevance found or requirement not fulfilled at all. Medium if the slightly matches the 
    requirement. High if the resume is a perfect match for the requirement.
    Strictly give response in json format. structure of json should be as below:
    {
    no_of_requirements:"number of requirements",
    match: {
    "req1":"low/med/high",
    "req2":"low/med/high
    }
    }
    Show only the json, not any text outside json.'''

    prompt_msg_2 = '''Evaluate if the resume of candidate fits each job requirement. Based on relevance rate on a 
    scale of 1-5. 1 for no relevance or requirement not fulfilled at all. 3 if the slightly matches the requirement. 
    5 if the resume is a perfect match for the requirement.
    Strictly give response in json format. structure of json should be as below:
    {
    no_of_requirements:"number of requirements",
    match: {
    "req1":"1/2/3/4/5",
    "req2":"1/2/3/4/5"
    }
    }
    Show only the json, not any text outside json.'''

    prompt_msg_3 = '''Evaluate if the resume of candidate fits each job requirement. Based on relevance rate it Very 
    Low, Low, Medium, High, Very High. Very Low for no relevance or requirement not fulfilled at all. Low if the 
    slightly matches the requirement. Medium if the resume is a good match for the requirement. High if the resume is 
    a perfect match for the requirement. Very High if the resume is an exceptional match for the requirement.
    Strictly give the response in json format. Structure of json should be as below:
    {
    no_of_requirements:"number of requirements",
    match: {
    "req1":"Very Low/Low/Medium/High/Very High",
    "req2":"Very Low/Low/Medium/High/Very High"
    }
    }
    Show only the json, not any text outside json.
    '''
    responses = []
    scores = []
    for i in range(accuracy):
        response = ollama.chat(model='llama3', messages=[
            {'role': 'user', 'content': resume_msg + resume_text + jd_msg + job_desc + prompt_msg},
        ])
        json_response = json.loads(extract_bracket_content(response['message']['content']))
        responses.append(json_response)
        score = 0

        total = 2 * json_response['no_of_requirements']
        for key in json_response['match']:
            if json_response['match'][key] == 'low':
                score += 0
            elif json_response['match'][key] == 'medium':
                score += 1
            elif json_response['match'][key] == 'high':
                score += 2

            print(score, total)
            scores.append(score * 100 / total)

        return sum(scores) / len(scores)
