# A simple example test

In this example we will create a server which doubles any number you pass it, and write some simple tests for it. You'll see how simple the YAML-based sysntax can be, and the three different ways you can run Tavern tests.

Here's what such a server might look like:

#### server.py

```python
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/double", methods=["POST"])
def double_number():
    r = request.get_json()

    try:
        number = r["number"]
    except (KeyError, TypeError):
        return jsonify({"error": "no number passed"}), 400

    try:
        double = int(number)*2
    except ValueError:
        return jsonify({"error": "a number was not passed"}), 400

    return jsonify({"double": double}), 200
```

There are two key things to test here: first, that it successfully doubles numbers and second, that it returns the corret error codes and messages.

To do this we will write two 'blocks', one for the success case and one for the error case. Each bloack can contain one or more tests, and each test has a name, a request and an expecyted response.

#### test_server.tavern.yaml

```
---

block_name: Make sure server doubles number properly

tests:
  - name: Make sure number is returned correctly
    request:
      url: http://localhost:5000/double
      json:
        number: 5
      method: POST
      headers:
        content-type: application/json
    response:
      status_code: 200
      body:
        double: 10

---

block_name: Check invalid inputs are handled

tests:
  - name: Make sure invalid numbers don't cause an error
    request:
      url: http://localhost:5000/double
      json:
        number: dkfsd
      method: POST
      headers:
        content-type: application/json
    response:
      status_code: 400
      body:
        error: a number was not passed

  - name: Make sure it raises an error if a number isn't passed
    request:
      url: http://localhost:5000/double
      json:
        wrong_key: 5
      method: POST
      headers:
        content-type: application/json
    response:
      status_code: 400
      body:
        error: no number passed

```

## Running the tests

Tests can be run in three different ways: from Python code, from the command line, or with Pytest. All three require Tavern to be installed.

### Using Python

```
from tavern.core import run

success = run("test_server.tavern.yaml", {})

if not success:
    print("Error running tests")

```

### Using the command line (`tavern-ci`)

```
$ tavern-ci --in-file test_server.tavern.yaml
$ echo $?
0
```

### Using Pytest

Just run pytest and point it to the folder containing the integration tests (or add it to `setup.cfg/tox.ini/etc`). It will automatically find the tests using Pytest's collection mechanism.

```
$ py.test
============================= test session starts ==============================
platform linux -- Python 3.5.2, pytest-3.2.0, py-1.4.34, pluggy-0.4.0
rootdir: /home/developer/project/tests, inifile: setup.cfg
plugins: tavern-0.0.1
collected 4 items 

test_server.tavern.yaml ..

===================== 2 passed, 2 skipped in 0.07 seconds ======================
```
