# Python Cloudy

**A Python utility that simplifies cloud configuration**

---

## Overview

Python Cloudy is a utility to simplify server cloud configuration and automation.

---

## Installation

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `git clone https://github.com/un33k/python-cloudy`
4. `pip install -e python-cloudy`
5. `cd python-cloudy/cloudy`
6. `fab -l`
7. *(Optional)* Create a `~/.cloudy` file based on the example in the `cfg` directory.

---

## Usage

- List all commands:
  ```
  fab -l
  ```
- Run a command:
  ```
  fab -H auto@10.10.10.198:22022 -i ~/.ssh/id_rsa.pub core.sys-uname
  ```
  ```
  fab recipe-generic-server.setup-server --cfg-file=./.cloudy.generic
  ```
  ```
  fab -H root@10.10.10.198 recipe-generic-server.setup-server --cfg-file=./.cloudy.generic,./.cloudy.admin
  ```
- *(...etc.)*

---

## Running the Tests

To run the tests against the current environment:

```
python test.py
```

---

## License

Released under the [MIT](LICENSE) license.

---

## Versioning

**X.Y.Z Versioning**

- `MAJOR` version: Incompatible API changes
- `MINOR` version: Backwards-compatible functionality
- `PATCH` version: Backwards-compatible bug fixes

---

## Sponsors

[Neekware Inc](https://neekware.com)

---

## Python Compatibility

Python Cloudy is compatible with Python versions 3.8 and above. Please ensure that your environment meets this requirement before installing.

---

## Development

To contribute to Python Cloudy, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear, descriptive messages.
4. Push your branch to your fork on GitHub.
5. Submit a pull request to the main repository, detailing your changes and the problem they solve.

Please ensure that your code adheres to the existing style and conventions used in the project.
