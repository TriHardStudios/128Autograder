from flask import Flask

app = Flask(__name__)

@app.route("/repos/CSCI128/128Autograder/tags")
def tags():
    return \
        [
            {"name": "1.0.0"},
            {"name": "2.0.0"}
        ]
