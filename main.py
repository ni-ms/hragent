import json
import shutil

import ollama
import pymupdf
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

import resume_evaluation
from utils import extract_bracket_content

app = FastAPI()

jobs = {}

prompt = '''Give a list of specific job requirements for this role strictly in json format. structure of json should 
be as below: { no_of_requirements:"number of requirements you identified", requirements: { "req1":"First requirement 
you identified", "req2":"Second requirement you identified", } } Show only the json, not any text outside json.'''


@app.get("/Status")
async def app_status():
    return 'App is running'


@app.post("/JD")
async def jd_parsing(jd: str = Form(...), name: str = Form(...)):
    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': jd + prompt}
    ])
    raw_response = response['message']['content']
    parsed_response = extract_bracket_content(raw_response)
    parsed_response = json.loads(parsed_response)
    requirements = parsed_response['requirements']
    new_requirements = {}
    for i, key in enumerate(requirements.keys()):
        new_requirements[f"req{i + 1}"] = requirements[key]
    parsed_response['requirements'] = new_requirements

    jobs[name] = parsed_response
    return JSONResponse(content=parsed_response)


@app.get("/JD_List")
async def jd_list():
    return jobs


@app.post("/Profile")
async def profile_parsing(name: str = Form(...), resume: UploadFile = File(...)):
    file_path = f"./resumes/{resume.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    resume_text = ""
    with pymupdf.open(file_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            resume_text += page.get_text()

    if name not in jobs:
        raise HTTPException(status_code=404, detail="Profile not found")

    response = resume_evaluation.resumeEvaluation(str(jobs[name]), resume_text, 1)
    return {"score": response}
