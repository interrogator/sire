"""
god help us for the following. It is so horrible that it gets its own quantantined
file, far away from the good code.

This data is used to remove uneeded lines from the project as best we can.

For example, if the user didn't want mypy, we should remove references to it,
for example in the travis cd.

Keys are the possibly excluded things. Values are a list of strings, starting at
the start of the line, to match and remove.
"""
BADLINES = dict(
    readme=[
        '    long_description=read("README.md"),',
        '    long_description_content_type="text/markdown",'
        "[bumpversion:file:README.md",
        r"search = > Version {current_version}",
        r"replace = > Version {new_version}",
    ],
    mkdocs=["[![readthedocs](https"],
    __init__=[
        "[bumpversion:file:{name}/__init__.py]",
        r'search = __version__ = "{current_version}"',
        r'replace = __version__ = "{new_version}"',
    ],
    flake8=["        - flake8", "flake8 "],
    isort=["        - isort -m 3 -tc -c", "isort -m 3 -tc"],
    mypy=["        - mypy "],
    virtualenv=["proj=$", 'source "venv-', "# use virtualenv"],
    git=[
        "# or",
        "git clone https",
        '    url="http://',
        "git push origin master",
        "# push to ",
    ],
    codecoverage=[
        "[![codecov.io](https",
        "        - coverage run -m unittest",
        "        - coverage report",
        "        - codecov",
        "      script:  # coverage",
    ],
    travis=["[![Build Status](https"],
    black=["[![Code style: black]", "        - black --check", "black "],
    setup=[
        "[bumpversion:file:setup.py]",
        r'search = version="{current_version}"',
        r'replace = version="{new_version}"',
    ],
    bumpversion=["bump2version $1", "# bump the version"],
)
