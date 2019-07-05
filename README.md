# sire: generate a new Python 3.7 project

> Version 1.0.2

[![Build Status](https://travis-ci.org/interrogator/sire.svg?branch=master)](https://travis-ci.org/interrogator/sire)
[![codecov.io](https://codecov.io/gh/interrogator/sire/branch/master/graph/badge.svg)](https://codecov.io/gh/interrogator/sire)
[![readthedocs](https://readthedocs.org/projects/sire/badge/?version=latest)](https://sire.readthedocs.io/en/latest/)
[![PyPI version](https://badge.fury.io/py/sire.svg)](https://badge.fury.io/py/sire)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

## Install sire

```bash
pip install sire
#or
git clone https://github.com/interrogator/sire && cd sire && python.setup.py install
```

## Usage

Bash:

```bash
sire --mkdocs --virtualenv <project_name>
# or
python -m sire.sire mkdocs virtualenv <project_name>
```

From inside Python (why?):

```python
from sire import sire
sire('project name', mkdocs=True, virtualenv=True)
```

Currently includes:

* Optional mkdocs
* Optional virtualenv
* git initialisation
* Python .gitignore
* .coveragerc
* .travis.yml
* requirements.txt (with black, isort etc)
* basic setup.py
* publish.sh (a script for running tests and authoring a new version)
* mypy.ini
* MIT License
* Empty CHANGELOG
* .pre-commit-config.yaml
* bumpversion.cfg

## Triva

*sire* actually generated itself.

## Contributing

I don't really expect other people to want this, but you are more than welcome to submit pull/feature requests anyway.
