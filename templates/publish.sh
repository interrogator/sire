#!/usr/bin/env bash

# fail on any error
set -e
echo "Doing $1 update"

# use python 3.7 virtualenv
proj=${PWD##*/}
source "venv-$proj/bin/activate"

# check formatting
flake8 {name}/* tests/* setup.py
black {name}/* tests/* setup.py --check
isort -m 3 -tc -c {name}/* tests/* setup.py

# run tests
python -m unittest

# remove old releases
rm -r -f build dist

# bump the version
bump2version $1

# make new releases
python setup.py bdist_egg sdist

# upload
twine upload dist/*

# push to github
git push origin master --follow-tags 
