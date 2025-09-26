# Easier API testing

[![Github Actions](https://github.com/taverntesting/tavern/actions/workflows/main.yml/badge.svg)](https://github.com/taverntesting/tavern/actions/workflows/main.yml) [![PyPi](https://img.shields.io/pypi/v/tavern.svg)](https://pypi.org/project/tavern/) [![Read the Docs](https://readthedocs.org/projects/pip/badge/?version=latest&style=flat)](https://tavern.readthedocs.io/en/latest/)


Tavern is a pytest plugin, command-line tool and Python library for automated
testing of APIs, with a simple, concise and flexible YAML-based syntax. It's
very simple to get started, and highly customisable for complex tests. Tavern
supports testing RESTful APIs as well as MQTT based APIs.

Tavern acts as a pytest plugin so that all you have to do is install pytest and
Tavern, write your tests in `.tavern.yaml` files, and run pytest. This means you
get access to the entire pytest ecosystem.

You can also integrate Tavern into your own test framework or continuous
integration setup using the Python library, or use the command line tool,
`tavern-ci` with bash scripts and cron jobs.

## Quickstart

First up run `pip install tavern`.

Then, let's create a basic test, `test_minimal.tavern.yaml`:

```yaml
---
# Every test file has one or more tests...
test_name: Get some fake data from the JSON placeholder API

# ...and each test has one or more stages (e.g. an HTTP request)
stages:
  - name: Make sure we have the right ID

    # Define the request to be made...
    request:
      url: https://jsonplaceholder.typicode.com/posts/1
      method: GET

    # ...and the expected response code and body
    response:
      status_code: 200
      # A JSON dict response
      json:
        id: 1
```

This file can have any name, but if you intend to use Pytest with Tavern, it
will only pick up files called `test_*.tavern.yaml`.

This can then be run like so:

```bash
$ pip install tavern
$ py.test test_minimal.tavern.yaml  -v
=================================== test session starts ===================================
platform linux -- Python 3.5.2, pytest-3.4.2, py-1.5.2, pluggy-0.6.0 -- /home/taverntester/.virtualenvs/tavernexample/bin/python3
cachedir: .pytest_cache
rootdir: /home/taverntester/myproject, inifile:
plugins: tavern-0.7.2
collected 1 item

test_minimal.tavern.yaml::Get some fake data from the JSON placeholder API PASSED   [100%]

================================ 1 passed in 0.14 seconds =================================
```

Tavern is not just limited to testing HTTP APIs however - it can also be used to
test MQTT, or you can mix MQTT commands inline with HTTP tests to test more
complex systems.

To learn more, check out the
[examples](https://taverntesting.github.io/examples) or the complete
[documentation](https://taverntesting.github.io/documentation). If you're
interested in contributing to the project take a look at the
[GitHub repo](https://github.com/taverntesting/tavern).

## Why not Postman, Insomnia or pyresttest etc?

Tavern is a focused tool which does one thing well: automated testing of APIs.

**Postman**, **Insomnia**, **Bruno**, etc. are excellent tools which cover a wide range of use-cases for RESTful APIs. However, specifically with regards to automated testing, Tavern has several advantages over Postman:
- A full-featured Python environment for writing easily reusable custom validation functions
- Testing of MQTT and gRCP based systems in tandem with RESTful APIS.
- Seamless integration with pytest to keep all your tests in one place
- A simpler, less verbose and clearer testing language

Tavern does not do many of the things Postman and Insomnia do. For example, Tavern does not have a GUI nor does it do API monitoring or mock servers. On the other hand, Tavern is free and open-source and is a more powerful tool for developers to automate tests.

## Questions and community

If you have any feature requests or if you've found a bug you can raise an
[issue on GitHub](https://github.com/taverntesting/tavern/issues).
