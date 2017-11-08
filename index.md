# Restful API testing

Tavern is a pytest plugin, command-line tool and Python library for automated testing of RESTful APIs, with a simple, concise and flexible YAML-based syntax. It's very simple to get started, and highly customisable for complex tests.

The best way to use Tavern is with [pytest](https://docs.pytest.org/en/latest/). Tavern comes with a pytest plugin so that literally all you have to do is install pytest and Tavern, write your tests in `.tavern.yaml` files and run pytest. This means you get access to all of the pytest ecosystem and allows you to do all sorts of things like regularly run your tests against a test server and report failures or generate HTML reports.

You can also integrate Tavern into your own test framework or continuous integration setup using the Python library, or use the command line tool, `tavern-ci` with bash scripts and cron jobs.

To learn more, check out the [examples](/examples) or the complete [documentation](/documentation). If you're interested in contributing to the project take a look at the [GitHub repo](https://github.com/taverntesting/tavern).

## Quickstart

```
$ pip install tavern
```

```yaml
# minimal_test.tavern.yaml

# Every test file has one or more tests...
test_name: Get some fake data from the JSON placeholder API

# ...and each test has one or more stages (e.g. an HTTP request)
stages:
  - name: Make sure we have the right ID

    # Define the request to be made...
      url: https://jsonplaceholder.typicode.com/posts/1
      method: GET

    # ...and the expected response code and body
    response:
      status_code: 200
      body:
        id: 1
```

```bash
$ tavern-ci --in-file minimal_test.tavern.yaml
```

## Why not Postman, Insomnia or pyresttest etc?

Tavern is a focused tool which does one thing well: automated testing of RESTful APIs.

**Postman** and **Insomnia** are excellent tools which cover a wide range of use-cases, and indeed we use Tavern alongside Postman. However, specifically with regards to automated testing, Tavern has several advantages over Postman:
- A full-featured Python environment for writing custom validation functions
- Seamless integration with pytest to keep all your tests in one place
- A simpler, less verbose and clearer testing language

Tavern does not do many of the things Postman and Insomnia do. For example, Tavern does not have a GUI nor does it do API monitoring or mock servers. On the other hand, Tavern is free and open-source and is a more powerful tool for developers to automate tests.

**pyresttest** is similar to Tavern but is no longer actively developed. Tavern also has several advantages over PyRestTest which overall add up to a better developer experience:

- Cleaner test syntax which is more intuitive, especially for non-developers
- Validation function are more flexible and easier to use
- Better explanations of why a test failed

## Acknowledgements

Tavern makes use of several excellent open-source projects:

- [pytest](https://docs.pytest.org/en/latest/), the testing framework Tavern intergrates with
- [requests](http://docs.python-requests.org/en/master/), for HTTP requests
- [YAML](http://yaml.org/) and [pyyaml](https://github.com/yaml/pyyaml), for the test syntax
- [pykwalify](https://github.com/Grokzen/pykwalify), for YAML schema validation
- [pyjwt](https://github.com/jpadilla/pyjwt), for decoding JSON Web Tokens
- [colorlog](https://github.com/borntyping/python-colorlog), for formatting terminal outputs


## Developed and maintained by [Overlock](https://overlock.io)

Overlock helps developers quickly find and fix bugs in distributed systems such as IoT deployments by gathering together exception information from end devices, gateways or servers. We're currently in beta - find out more at [overlock.io](https://overlock.io)
