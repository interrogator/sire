# sire

> *sire* is a command that generates Python 3.7 project templates, with git, travis, mypy (etc.) support.

> Version 1.0.4

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

Use the `-m`, `-v` and `-g` flags to configure *mkdocs*, *virtualenv* and *git*.

`-g` should be one of: `'github'`, `'gitlab'` or `'bitbuckeet'`.

The `-e` flag takes a comma-separated list of items to exclude.

```bash
sire --mkdocs --virtualenv --git=github --exclude=mypy,LICENSE <project_name>
```

Result of `sire -v -g=bitbucket -m demo`:

```
demo
├── demo
│   ├── demo.py
│   └── __init__.py
├── docs
│   ├── about.md
│   └── index.md
├── .git
│   └── <the usual .git contents>
├── tests
│   ├── tests.py
│   └── __init__.py
├── venv-demo
│   └── <the usual venv contents>
├── .bumpversion.cfg
├── CHANGELOG.md
├── .coveragerc
├── .flake8
├── .gitignore
├── LICENSE
├── mkdocs.yml
├── mypy.ini
├── .pre-commit-config.yaml
├── publish.sh
├── README.md
├── .readthedocs.yaml
├── requirements.txt
├── setup.py
└── .travis.yml
```

You can also run *sire* from within Python, though there's really no compelling reason to do so. Note that here you pass all excludes with the `exclude` argument, including *git*, *mkdocs* and *virtualenv*.

```python
from sire import sire
sire('project_name', exclude={'mypy', 'git'}, interactive=False)
```

## Trivia

* *sire* actually generated itself.

## Contributing

I don't really expect many other people to want this, because it's mostly tailored to my specific ideas about how a Python project should look. That said, if you do find this project useful, you are more than welcome to submit pull/feature requests!

There are dozens of possible new features that could be added, which I'd personally quite like:

* a `--license` option, to choose the correct license file
* Setting git remote automatically (get github username from git global config?)
* Deleting irrelevant strings --- if no *codecoverage*, remove the associated badge for example
* Probably more code could be automatically generated and added for the main and test `.py` files

While I'd love to have these in *sire*, coding them will take me longer than doing it manually a few times. So, unless this repo somehow becomes popular or finds some new contributors, don't expect any of this stuff to get done in a hurry, unless you add it yourself.