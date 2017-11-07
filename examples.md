# Examples

## 1) The simplest possible test

To show you just how simple a Tavern test can be, here's one which uses the JSON Placeholder API at [jsonplaceholder.typicode.com](https://jsonplaceholder.typicode.com/). To try it, create a new file called `minimal_test.tavern.yaml` with the following:

```yaml
test_name: Get some fake data from the JSON placeholder API

steps:
  - name: Make sure we have the right ID
    request:
      url: https://jsonplaceholder.typicode.com/posts/1
      method: GET
    response:
      status_code: 200
      body:
        id: 1
```

Next, install Tavern if you have not already:

```bash
$ pip install tavern
```

In most circumstances you will be using Tavern with pytest but you can also run it using the Tavern command-line interface, `tavern-ci`, which is installed along with Tavern:

```bash
$ tavern-ci --in-file minimal.tavern.yaml
```

Run `tavern-ci --help` for more usage information.

## 2) Testing a simple server

In this example we will create a server with a single route which doubles any number you pass it, and write some simple tests for it. You'll see how simple the YAML-based syntax can be, and the three different ways you can run Tavern tests.

Here's what such a server might look like:

```python
# server.py

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

Run the server using Flask:

```bash
$ export FLASK_APP=server.py
$ flask run
```

There are two key things to test here: first, that it successfully doubles numbers and second, that it returns the correct error codes and messages. To do this we will write two tests, one for the success case and one for the error case. Each test can contain one or more steps, and each step has a name, a request and an expected response.

```yaml
# test_server.tavern.yaml

---

test_name: Make sure server doubles number properly

steps:
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

test_name: Check invalid inputs are handled

steps:
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

The tests can be run in three different ways: from Python code, from the command line, or with pytest. The most common way is to use pytest. All three require Tavern to be installed.

If you run pytest in a folder containing `test_server.tavern.yaml` it will automatically find the file and run the tests. Otherwise, you will need to point it to the folder containing the integration tests or add it to `setup.cfg/tox.ini/etc` so that Pytest's collection mechanism knows where to look.

```bash
$ py.test
============================= test session starts ==============================
platform linux -- Python 3.5.2, pytest-3.2.0, py-1.4.34, pluggy-0.4.0
rootdir: /home/developer/project/tests, inifile: setup.cfg
plugins: tavern-0.0.1
collected 4 items 

test_server.tavern.yaml ..

===================== 2 passed, 2 skipped in 0.07 seconds ======================
```

The Python library allows you to include Tavern tests in deploy scripts written in Python, or for use with a continuous integration setup:

```python
from tavern.core import run

success = run("test_server.tavern.yaml", {})

if not success:
    print("Error running tests")
```

The command line tool is useful for bash scripting, for example if you want to verify that an API is works before deploying it, or for cron jobs. 

```bash
$ tavern-ci --in-file test_server.tavern.yaml
$ echo $?
0
```

## 3) Multi-step tests

The final example uses a more complex test server which requires the user to log in, save the token it returns and use it for all future requests. It also has a simple database so we can check that data we send to it is successfully returned.

[Here is the example server we will be using.](/server)

To test this behaviour we can use multiple tests in a row, keeping track of variables between them, and ensuring the server state has been updated as expected.

```yaml
test_name: Make sure server saves and returns a number correctly

steps:
  - name: login
    request:
      url: http://localhost:5000/login
      json:
        user: test-user
        password: correct-password
      method: POST
      headers:
        content-type: application/json
    response:
      status_code: 200
      body:
        $ext:
          function: tavern.testutils.helpers:validate_jwt
          extra_kwargs:
            jwt_key: "token"
            key: CGQgaG7GYvTcpaQZqosLy4
            options:
              verify_signature: true
              verify_aud: false
      headers:
        content-type: application/json
      save:
        body:
          test_login_token: token

  - name: post a number
    request:
      url: http://localhost:5000/numbers
      json:
        name: smallnumber
        number: 123
      method: POST
      headers:
        content-type: application/json
        Authorization: "bearer {test_login_token:s}"
    response:
      status_code: 201
      body:
        {}
      headers:
        content-type: application/json

  - name: Make sure its in the db
    request:
      url: http://localhost:5000/numbers
      params:
        name: smallnumber
      method: GET
      headers:
        content-type: application/json
        Authorization: "bearer {test_login_token:s}"
    response:
      status_code: 200
      body:
        number: 123
      headers:
        content-type: application/json
```

This example illustrates three major parts of the Tavern syntax: saving data, using that data in later requests and using validation functions. 

### Saving data for later requests

```yaml
response:
  save:
    body:
      <variable name>: <value to assign>
```

To save a piece of data returned from an API call, use the `save` key in the response object. For each piece of data you want to save, you have to specify which part of the response you want to save by passing the key name and what you want to refer to the variable as in later tests. You can save data from the `body`, `headers`.

This example assigns the value of `body.token` to the variable `test_login_token` and the redirect location to `next_redirect_location`.

```yaml
save:
  body:
    test_login_token: token
  headers:
    next_redirect_location: location
```

### Using saved data

```yaml
<key>: "{<variable name>:<type code>}"
```

Saved data can be used in later tests using Python's [string formatting
syntax](https://docs.python.org/2/library/string.html#format-string-syntax). The
variable to be used is encased in curly brackets and an optional
[type code](https://docs.python.org/2/library/string.html#format-specification-mini-language)
can be passed after a colon.

```yaml
headers:
  Authorization: "Bearer {test_login_token:s}"
```

### External functions

Python functions can be called inside tests to perform operations on data which
is more advanced than can be expressed in YAML. These are of the form:

```yaml
$ext:
  function: <path to module>:<name of function>
  extra_kwargs:
    <key>: <value>
    <key>:
      <nested key>: <value>
      <nested key>: <value>
```

To use a python function as a validation function, add it to the response body,
headers, or redirect query parameters block inside a `$ext` key. You must
specify the path to the module containing the function (for example, all
built-in validation functions are located at `tavern.testutils.helpers`) and the
name of the function in the `function` key.

The first argument of every validation function is the response, and further
arguments can be passed in by defining them in `extra_args` and `extra_kwargs`.
External functions can also be used for saving data for use in future tests.

## Further reading

For more detailed information on how to use Tavern and how it works, take a look
at the [documentation](/documentation). To see the source code, suggest
improvements or even contribute a pull request check out the [GitHub
repository](https://github.com/taverntesting/tavern).
