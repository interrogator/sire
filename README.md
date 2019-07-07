# sire

> *sire* is a command that generates Python 3.7 project templates, with git, travis, mypy (etc.) support.

> Version 1.0.3

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

```bash
sire --mkdocs --virtualenv --git --exclude=mypy <project_name>
```

## Alternative usages (not recommended)

As Python module:

```bash
python -m sire.sire mkdocs virtualenv <project_name>
```

Or from inside Python (why?):

```python
from sire import sire
sire('project_name', mkdocs=True, virtualenv=True, git=True)
```

### What gets generated

Pure Python:

* proj_name/proj_name.py
* proj_name/__init__.py
* setup.py
* requirements.txt (with black, isort, flake8 etc)
* tests/tests.py

Optional extras:

* mkdocs (.readthedocs.yaml, ./docs, .mkdocs.yml)
* virtualenv virtualenv (with dependencies installed)
* git (.git, .gitignore, .pre-commit-config.yaml)

Each of these has an associated flag:

```bash
sire -v/--virtualenv -m/--mkdocs -g/--git projname
```

Other files

* .coveragerc
* .travis.yml
* publish.sh (a script for running tests and authoring a new version)
* mypy.ini
* MIT License
* Empty CHANGELOG
* .bumpversion.cfg

If you want to skip any of these files, use the `--exclude` option with comma separation:

```bash
sire --exclude=travis,setup.py,mypy projname
```

## Trivia

* *sire* actually generated itself.

## Contributing

I don't really expect many other people to want this, because it's mostly tailored to my specific ideas about how a Pthon project should look. That said, if you do find this projet useful, you are more than welcome to submit pull/feature requests!

There are dozens of possible new features that could be added, which I'd personally quite like:

* a `--license` option, to choose the correct license file
* Setting git remote automatically (get github username from git global config?)
* Deleting irrelevant strings --- if no codecoverage, remove the associated badge for example
* Probably more code could be automatically generated and added for the main and test .py files

While I'd love to have these in *sire*, coding them will take me longer than doing it manually a few times. So, unless this repo somehow becomes popular or finds some new contributors, don't expect any of this stuff to get done in a hurry, unless you add it yourself.