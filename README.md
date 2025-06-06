# Python Cloudy

**A Python utility that simplifies cloud configuration**

---

## Overview

Python Cloudy is a utility to simplify server cloud configuration and automation.

---

## Installation

1. `virtualenv cloudy`
2. `source cloudy/bin/activate`
3. `cd cloudy`
4. `git clone https://github.com/un33k/python-cloudy`
5. `pip install -e python-cloudy`
6. `cd python-cloudy/cloudy`
7. `fab -l`
8. *(Optional)* Create a `~/.cloudy` file based on the example in the `cfg` directory.

---

## Usage

- List all commands:
  ```
  fab -l
  ```
- Run a command:
  ```
  fab -H 10.10.10.10 -i ~/.ssh/key.pem sys_uname
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
