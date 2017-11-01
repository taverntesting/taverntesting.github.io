# Tavern
## Restful API testing

Tavern is a free and open source command-line tool and Python library for automated testing of RESTful APIs.

Write tests in a simple, concise and flexible YAML-based format and run them from your own code, from Pytest or from the command line.

### Pytest integration

Tavern integrates with Pytest. This means you get access to all of the Pytest ecosystem. This means you can do all sorts of things like:
- Regularly run your tests against a test server and report failures
- Generate reports  

### Why not Postman or Insomnia?

Tavern is a focused tool for developers which does one thing well: automated testing of RESTful APIS.

Postman and Insomnia are excellent tools which cover a wide range of use-cases, and indeed we use Tavern alongside Postman. However, specifically with regards to automated testing, we found Postman to have several limitations:
- Limited library support, even for simple tasks like decoding a JWT
- Lots of repeated code for custom functions
- Challenging to integrate with GitLab and other continuous integration tools
- Verbose testing language and export

Tavern does not do many of the things Postman and Insomnia do. For example, Tavern does not have a GUI nor does it do API monitoring or mock servers.

On the other hand, Tavern is free and open-source and is a more powerful tool for developers to automate tests.
