"""Saving the code str form in a json file."""
import os
import json

FILE = "template.json"
SCRIPT_DIR = os.path.dirname((os.path.realpath(__file__)))
FOLDER_PATH = os.path.join(SCRIPT_DIR, "samples")
DOCUMENT = os.path.join(FOLDER_PATH, FILE)


def read_template():
    """ "Reads the template file"""
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
    if not os.path.exists(DOCUMENT) or os.path.getsize(DOCUMENT) == 0:
        write_template({})
    with open(DOCUMENT, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def write_template(data):
    """Writes the template to the json file"""
    with open(DOCUMENT, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=4)


def ssr_template():
    """Python template for ssr"""
    code = """from flask import Flask, render_template
app = Flask(__name__)
@app.route('/')
def home():
    data = {
        'title': 'My SSR Flask App',
        'content': 'Welcome to my SSR Flask App!',
    }
    return render_template('index.html', **data)
if __name__ == '__main__':
    app.run()"""
    html = """<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ content }}</h1>
</body>
</html>"""
    data = read_template()
    ssr_dict = {"code": code, "html": html}
    data["ssr"] = ssr_dict

    write_template((data))


def csr_template():
    """Python template for csr"""
    code = """from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    # Fetch data from the the database, for example
    data = {
        'name': 'John Doe',
        'age': 30,
        'email': 'johndoe@example.com'
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run()"""
    javascript = """var request = new XMLHttpRequest();
request.open('GET', '/api/data', true);

// Define what happens when the request succeed
request.onload = function() {
  if (request.status === 200) {
    // Use the data to update the UI, or in this case, just log into the screen
    var data = JSON.parse(request.responseText);
    console.log(data);
  }
};

// Send the request
request.send();"""

    csr_dict = {"code": code, "javascript": javascript}
    data = read_template()
    data["csr"] = csr_dict
    write_template(data)


def get_ssr_code():
    """Returns the ssr code"""
    data = read_template()
    ssr = data["ssr"]
    return ssr["code"]


def get_ssr_html():
    """Returns the ssr html"""
    data = read_template()
    ssr = data["ssr"]
    return ssr["html"]


if __name__ == "__main__":
    ssr_template()
    csr_template()
