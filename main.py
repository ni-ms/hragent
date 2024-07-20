import json

import flask
import ollama
import pymupdf
from flask import Flask, request, jsonify

import resume_evaluation
from utils import extract_bracket_content

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

jobs = {}

prompt = '''Give a list of specific job requirements for this role strictly in json format. structure of json should be as below:
{
no_of_requirements:"number of requirements you identified",
requirements: {
"req1":"First requirement you identified",
"req2":"Second requirement you identified",
}
}
Show only the json, not any text outside json.
'''


@app.route("/Status", methods=["GET"])
def AppStatus():
    return 'App is running'


@app.route("/JD", methods=["POST"])
def JDParsing():
    if request.method == "POST":
        job_description = request.form["jd"]
        job_name = request.form["name"]

        response = ollama.chat(model='llama3', messages=[
            {'role': 'user', 'content': job_description + prompt}
        ])
        raw_response = response['message']['content']
        parsed_response = extract_bracket_content(raw_response)

        # If the keys in requirements sub dictionary are not in the format of req1, req2, req3, etc. then convert them to req1, req2, req3, etc.
        parsed_response = json.loads(parsed_response)
        requirements = parsed_response['requirements']
        new_requirements = {}
        for i, key in enumerate(requirements.keys()):
            new_requirements[f"req{i + 1}"] = requirements[key]
        parsed_response['requirements'] = new_requirements
        # Convert to string

        print(parsed_response)

        jobs[job_name] = parsed_response
        parsed_response = jsonify(parsed_response)
        headers = {
            'Content-Type': 'application/json'
        }
        parsed_response.headers = headers
        return parsed_response
    else:
        return "invalid request"


@app.route("/JD_List", methods=["GET"])
def JDList():
    if request.method == "GET":
        jdl_response = flask.Response(json.dumps(jobs))
        headers = {
            'Content-Type': 'application/json'
        }
        jdl_response.headers = headers
        return jdl_response
    else:
        return "invalid request"


@app.route("/Profile", methods=["POST"])
def ProfileParsing():
    if request.method == "POST":
        profile_name = request.form["name"]
        file = request.files["resume"]

        # Save the uploaded PDF file to a temporary location
        file_path = f"./resumes/{file.filename}"
        file.save(file_path)

        # Open the PDF file and extract text
        resume_text = ""
        with pymupdf.open(file_path) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf.load_page(page_num)
                resume_text += page.get_text()

        # Optionally, delete the temporary file after processing
        # os.remove(file_path)

        response = resume_evaluation.resumeEvaluation(str(jobs[profile_name]), resume_text, 1)
        response = {"score": response}
        response = json.dumps(response)
        response = jsonify(response)
        headers = {
            'Content-Type': 'application/json'
        }
        response.headers = headers
        return response
    else:
        return "invalid request"


if __name__ == "__main__":
    app.run(host="localhost", port=8080)
