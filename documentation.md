# Documentation

More documentation is coming soon. Watch this space!

## External functions

There are two external functions built in to Tavern: `validate_jwt` and
`validate_pykwalify`.

`validate_jwt` takes the key of the returned JWT in the body as `jwt_key`, and
additional arguments that are passed directly to the `decode` method in the
[PyJWT](https://github.com/jpadilla/pyjwt/blob/master/jwt/api_jwt.py#L59)
library. **NOTE: Make sure the keyword arguments you are passing are correct
or PyJWT will silently ignore them. In future, this function will likely be
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

External functions can also be used to save data from the response. For example,
the built in `validate_jwt` function also returns the decoded token as a
dictionary wrapped in a [Box](https://pypi.python.org/pypi/python-box/) object,
which allows dot-notation access to members. This means that the contents of the
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
      # make sure a token exists
      $ext: &validate_jwt_anchor
        function: tavern.testutils.helpers:validate_jwt
        extra_kwargs:
          jwt_key: "token"
          options:
            verify_signature: false
    save:
      body:
        # Saves a jwt token returned as 'token' in the body as 'jwt' in the test
        # configuration for use in future tests
        $ext:
          # Use the same block
          <<: *validate_jwt_anchor

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
- etc.

## Anchors between documents

A lot of tests will require using the same step multiple times, such as logging
in to a server before running tests or simply running the same request twice in
a row to make sure the same (or a different) response is returned.

Anchors in YAML can be used to do things like this within the same document:

```yaml
# input.yaml
---
top: &top_anchor
  a: b
  c: d
  e: f

bottom:
  <<: *top_anchor
```
If we load this file with a script like this:

```python
#!/usr/bin/env python

# load.py
import yaml

with open("input.yaml", "r") as yfile:
    print(yaml.load(yfile.read()))
```
We get:
```
$ python test.py
{'top': {'a': 'b', 'e': 'f', 'c': 'd'}, 'bottom': {'a': 'b', 'e': 'f', 'c': 'd'}}
```

This does not however work if there are different documents in the yaml file:

```yaml
# input.yaml
---
top: &top_anchor
  a: b
  c: d
  e: f

---

bottom:
  <<: *top_anchor
```

```
$ python test.py
Traceback (most recent call last):
  File "test.py", line 4, in <module>
    print(yaml.load(yfile.read()))
  File "/home/michael/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/__init__.py", line 72, in load
    return loader.get_single_data()
  File "/home/michael/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/constructor.py", line 35, in get_single_data
    node = self.get_single_node()
  File "/home/michael/.virtualenvs/tavern/lib/python3.5/site-packages/yaml/composer.py", line 43, in get_single_node
    event.start_mark)
yaml.composer.ComposerError: expected a single document in the stream
  in "<unicode string>", line 3, column 1:
    top: &top_anchor
    ^
but found another document
  in "<unicode string>", line 8, column 1:
    ---
    ^
```

This poses a bit of a problem for running our integration tests. If we want to
log in at the beginning of each test, or if we want to qury some user
information which is then operated on for each test, we don't want to copy paste
the same code within the same file.

For this reason, Tavern will preserve anchors across documents **within the same
file**. Then we can do something more like this:

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
or is used on every test (eg, login information). You might also want to run the
same tests with different sets of input data.

Because of this, external files can also be included which contain simple
key: value data to be used in other tests.

Including a file in every test can be done by using a `!include` directive:

```yaml
# includes.yaml
---

name: Common test information
description: Login information for test server

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
