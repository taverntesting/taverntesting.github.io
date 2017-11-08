# Documentation

If you haven't already, it's worth looking through the [examples](/examples)
before diving into this.

## Contents

- [Anatomy of a test](#anatomy-of-a-test)
    - [Request](#request)
    - [Response](#response)
- [Calling external functions](#calling-external-functions)
    - [Built-in validators](#built-in-validators)
    - [Saving data with external functions](#saving-data-with-external-functions)
- [Anchors between documents](#anchors-between-documents)
- [Including external files](#including-external-files)
    - [Including external files via the command line](#including-external-files-via-the-command-line)

## Anatomy of a test

Tests are defined in YAML with a **test_name**, one or more **stages**, each of
which has a **name**, a **request** and a **response**. Taking the simple example:

```yaml
test_name: Get some fake data from the JSON placeholder API

stages:
  - name: Make sure we have the right ID
    request:
      url: https://jsonplaceholder.typicode.com/posts/1
      method: GET
    response:
      status_code: 200
      body:
        id: 1
      save:
        body:
          returned_id: id
```

If using the pytest plugin (the recommended way of using Tavern), this needs to
be in a file called `test_x.tavern.yaml`, where `x` is a description of the
contained tests.

**test_name** is, as expected, the name of that test. If the pytest plugin is
being used to run integration tests, this is what the test will show up as in
the pytest report, for example:

```
tests/integration/test_simple.tavern.yaml::Get some fake data from the JSON placeholder API
```

This can then be selected with the `-k` flag to pytest - e.g. pass `pytest -k fake`
to run all tests with 'fake' in the name.

**stages** is a list of the stages that make up the test. A simple test might
just be to check that an endpoint returns a 401 with no login information. A
more complicated one might be:

1. Log in to server
  - `POST` login information in body
  - Expect login details to be returned in body
2. Get user information
  - `GET` with login information in `Authorization` header
  - Expect user information returned in body
3. Create a new resource with that user information
  - `POST` with login information in `Authorization` header and user information in body
  - Expect a 201 with the created resource in the body
4. Make sure it's stored on the server
  - `GET` with login information in `Authorization` header
  - Expect the same information returned as in the previous step

The **name** of each stage is a description of what is happening in that
particular test.

### Request

The **request** describes what will be sent to the server. The keys for this are
passed directly to the
[requests](http://docs.python-requests.org/en/master/api/#requests.request)
library (after preprocessing) - at the moment the only supported keys are:

- `url` - a string, including the protocol, of the address of the server that
  will be queried
- `json` - a mapping of (possibly nested) key: value pairs/lists that will be
  converted to JSON and sent as the request body.
- `params` - a mapping of key: value pairs that will go into the query
  parameters.
- `data` - a mapping of key: value pairs that will go into the body as
  application/x-www-url-formencoded data.
- `headers` - a mapping of key: value pairs that will go into the headers. Defaults
  to adding a `content-type: application/json` header.
- `method` - one of GET, POST, PUT, or DELETE. Defaults to GET if not defined

For more information, refer to the [requests
documentation](http://docs.python-requests.org/en/master/api/#requests.request).

### Response

The **response** describes what we expect back. There are a few keys for verifying
the response:

- `status_code` - an integer corresponding to the status code that we expect.
  Defaults to `200` if not defined.
- `body` - Assuming the response is json, check the body against the values
  given. Expects a mapping (possibly nested) key: value pairs/lists.
  This can also use an external check function, described further down.
- `headers` - a mapping of key: value pairs that will be checked against the
  headers.
- `redirect_query_params` - Checks the query parameters of a redirect url passed
  in the `location` header (if one is returned). Expects a mapping of key: value
  pairs. This can be useful for testing implementation of an OpenID connect
  provider, where information about the request may be returned in redirect
  query parameters.

The **save** block can save values from the response for use in future requests.
Things can be saved from the body, headers, or redirect query parameters. When
used to save something from the json body, this can also access dictionaries
and lists recursively. If the response is:

```json
{
    "thing": {
        "nested": [
            1, 2, 3, 4
        ]
    }
}
```

This can be saved into the value `first_val` with this response block:

```yaml
response:
  save:
    body:
      fourth_val: thing.nested.0
```

It is also possible to save data using function calls, explained below.

For a more formal definition of the schema that the tests are validated against,
check `tavern/schemas/tests.schema.yaml` in the main Tavern repository.

## Calling external functions

Not every response can be validated simply by checking the values of keys, so with
Tavern you can call external functions to validate responses and save decoded data.
You can write your own functions or use those built in to Tavern. Each function
should take the response as its first argument, and you can pass extra arguments
using the **extra_kwargs** key.

### Built-in validators

There are two external functions built in to Tavern: `validate_jwt` and
`validate_pykwalify`.

`validate_jwt` takes the key of the returned JWT in the body as `jwt_key`, and
additional arguments that are passed directly to the `decode` method in the
[PyJWT](https://github.com/jpadilla/pyjwt/blob/master/jwt/api_jwt.py#L59)
library. **NOTE: Make sure the keyword arguments you are passing are correct
or PyJWT will silently ignore them. In thr future, this function will likely be
changed to use a different library to avoid this issue.**

```yaml
# Make sure the response contains a key called 'token', the value of which is a
# valid jwt which is signed by the given key.
response:
  body:
    $ext:
      function: tavern.testutils.helpers:validate_jwt
      extra_kwargs:
        jwt_key: "token"
        key: CGQgaG7GYvTcpaQZqosLy4
        options:
          verify_signature: true
          verify_aud: false
```

`validate_pykwalify` takes a
[pykwalify](http://pykwalify.readthedocs.io/en/master/) schema and verifies the
body of the response against it.

```yaml
# Make sure the response matches the given schema - a sequence of dictionaries,
# which has to contain a user name and may contain a user number.
response:
  body:
    $ext:
      function: tavern.testutils.helpers:validate_pykwalify
      extra_kwargs:
        schema:
          type: seq
          required: True
          sequence:
          - type: map
            mapping:
              user_number:
                type: int
                required: False
              user_name:
                type: str
                required: True
```

### Saving data with external functions

An external function can also be used to save data from the response. To do this,
the function must return a dict where each key either points to a single value or
to an object which is accessible using dot notation. The easiest way to do this
is to return a [Box](https://pypi.python.org/pypi/python-box/) object. Each key in
the returned object will be saved as if it had been specified separately in the
**save** object. The function is called in the same way as a validator function,
in the **$ext** key of the **save** object.

Say that we have a server which returns a response like this:

```json
{
    "user": {
        "name": "John Smith",
        "id": "abcdef12345",
    }
}
```

If our test function extracts the key `name` from the response body:

```python
# utils.py
def test_function(response):
    return {"test_user_name": response.json()["user"]["name"]}
```

We would use it in the **save** object like this:

```yaml
save:
  $ext:
    function: utils:test_function
  body:
    test_user_id: user.id
```

In this case, both `{test_user_name}` and `{test_uer_id}` are available for use
in later requests.

For a more practical example, the built in `validate_jwt` function also returns the
decoded token as a dictionary wrapped in a [Box](https://pypi.python.org/pypi/python-box/)
object, which allows dot-notation access to members. This means that the contents of the
token can be used for future requests.

For example, if our server saves the user ID in the 'sub' field of the JWT:

```yaml
- name: login
  request:
    url: http://server.com/login
    json:
      username: test_user
      password: abc123
  response:
    status_code: 200
    body:
      # Make sure a token exists
      $ext:
        function: tavern.testutils.helpers:validate_jwt
        extra_kwargs:
          jwt_key: "token"
          options:
            verify_signature: false
    save:
      # Saves a jwt token returned as 'token' in the body as 'jwt'
      # in the test configuration for use in future tests
      $ext:
        function: tavern.testutils.helpers:validate_jwt
        extra_kwargs:
          jwt_key: "token"
          options:
            verify_signature: false

- name: Get user information
  request:
    url: "http://server.com/info/{jwt.sub}"
    ...
  response:
    ...
```

Ideas for other helper functions which might be useful:

- Making sure that the response matches a database schema
- Making sure that an error returns the correct error text in the body
- Decoding base64 data to extract some information for use in a future query
- Validate templated HTML returned from an endpoint using an XML parser
- etc.

## Resuing requests and YAML fragments

A lot of tests will require using the same step multiple times, such as logging
in to a server before running tests or simply running the same request twice in
a row to make sure the same (or a different) response is returned.

Anchors are a feature of YAML which allows you to reuse parts of the code. Define
an anchor using  `&name_of_anchor`. This can then be assigned to another object
using `new_object: *name_or_anchor`, or they can be used to extend objects using
`<<: *name_of_anchor`.

```yaml
# input.yaml
---
first: &top_anchor
  a: b
  c: d

second: *top_anchor

third:
  <<: *top_anchor
  c: overwritten
  e: f
```

If we convert this to JSON, for example with a script like this:

```python
#!/usr/bin/env python

# load.py
import yaml
import json

with open("input.yaml", "r") as yfile:
    for doc in yaml.load_all(yfile.read()):
        print(json.dumps(doc, indent=2))
```

We get something like the following:

```
{
  'first': {
    'a': 'b',
    'c': 'd'
  },
  'second': {
    'a': 'b',
    'c': 'd'
  },
  'third': {
    'a': 'b',
    'c': 'overwritten',
    'e': 'f'
  }
}
```

This does not however work if there are different documents in the yaml file:

```yaml
# input.yaml
---
first: &top_anchor
  a: b
  c: d

second: *top_anchor

---

third:
  <<: *top_anchor
  c: overwritten
  e: f
```

```
$ python test.py
{
  "second": {
    "c": "d",
    "a": "b"
  },
  "first": {
    "c": "d",
    "a": "b"
  }
}
Traceback (most recent call last):
  File "test.py", line 8, in <module>
    for doc in yaml.load_all(yfile.read()):
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/__init__.py", line 84, in load_all
    yield loader.get_data()
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/constructor.py", line 31, in get_data
    return self.construct_document(self.get_node())
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/composer.py", line 27, in get_node
    return self.compose_document()
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/composer.py", line 55, in compose_document
    node = self.compose_node(None, None)
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/composer.py", line 84, in compose_node
    node = self.compose_mapping_node(anchor)
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/composer.py", line 133, in compose_mapping_node
    item_value = self.compose_node(node, item_key)
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/composer.py", line 84, in compose_node
    node = self.compose_mapping_node(anchor)
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/composer.py", line 133, in compose_mapping_node
    item_value = self.compose_node(node, item_key)
  File "/home/cooldeveloper/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/composer.py", line 69, in compose_node
    % anchor, event.start_mark)
yaml.composer.ComposerError: found undefined alias 'top_anchor'
  in "<unicode string>", line 12, column 7:
      <<: *top_anchor
```

This poses a bit of a problem for running our integration tests. If we want to
log in at the beginning of each test, or if we want to query some user
information which is then operated on for each test, we don't want to copy paste
the same code within the same file.

For this reason, Tavern will override the default YAML behaviour and preserve anchors
across documents **within the same file**. Then we can do something more like this:

```yaml
---
test_name: Make sure user location is correct

stages:
  - &test_user_login_anchor
    # Log in as user and save the login token for future requests
    name: Login as test user
    request:
      url: http://test.server.com/user/login
      method: GET
      json:
        username: test_user
        password: abc123
    response:
      status_code: 200
      save:
        body:
          test_user_login_token: token
      body:
        $ext:
          function: tavern.testutils.helpers:validate_jwt
          extra_kwargs:
            jwt_key: "token"
            options:
              verify_signature: false

  - name: Get user location
    request:
      url: http://test.server.com/locations
      method: GET
      headers:
        Authorization: "{test_user_login_token}"
    response:
      status_code: 200
      body:
    location:
          road: 123 Fake Street
          country: England

---
test_name: Make sure giving premium works

stages:
  # Use the same block to log in across documents
  - *test_user_login_anchor

  - name: Assert user does not have premium
    request: &has_premium_request_anchor
      url: http://test.server.com/user_info
      method: GET
      headers:
        Authorization: "{test_user_login_token}"
    response:
      status_code: 200
      body:
        has_premium: false

  - name: Give user premium
    request:
      url: http://test.server.com/premium
      method: POST
      headers:
        Authorization: "{test_user_login_token}"
    response:
      status_code: 200

  - name: Assert user now has premium
    request:
      # Use the same block within one document
      <<: *has_premium_request_anchor
    response:
      status_code: 200
      body:
        has_premium: true
```

## Including external files

Even with being able to use anchors within the same file, there is often some
data which either you want to keep in a separate (possibly autogenerated) file,
or is used on every test (e.g. login information). You might also want to run the
same tests with different sets of input data.

Because of this, external files can also be included which contain simple
key: value data to be used in other tests.

Including a file in every test can be done by using a `!include` directive:

```yaml
# includes.yaml
---

# Each file should have a name and description
name: Common test information
description: Login information for test server

# Variables should just be a mapping of key: value pairs
variables:
  protocol: https
  host: www.server.com
  port: 1234
```

```yaml
# tests.tavern.yaml
---
test_name: Check server is up

includes:
  - !include includes.yaml

stages:
  - name: Check healthz endpoint
    request:
      method: GET
      url: "{protocol:s}://{host:s}:{port:d}"
    response:
      status_code: 200
```

As long as includes.yaml is in the same folder as the tests, the variables will
automatically be loaded and available for formatting as before. Multiple include
files can be specified.

### Including external files via the command line

If you do want to run the same tests with a different input data, this can be
achieved by passing in a global configuration.

Using the `tavern-ci` tool or pytest, this can be passed in at the command line
using the `--tavern-global-cfg` flag. The file given will be loaded and used as
before.
