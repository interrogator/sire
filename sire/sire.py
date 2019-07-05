#!/usr/bin/env python

"""
sire: create a new python3.7 project using all the extra stuff i like.
"""

import os
import shutil
import stat
import sys

TEMPLATES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
assert os.path.isdir(TEMPLATES)


class SafeDict(dict):
    """
    Need a custom object to not error when formatting files that contain {var}
    """

    def __missing__(self, key):
        return "{" + key + "}"


def write(proj, outpath):
    """
    Get the filename from outpath
    read it from templates dir
    add project name to anywhere {name} appears in doc
    write to outpath
    """
    fname = os.path.basename(outpath)
    template = os.path.join(TEMPLATES, fname)
    with open(template, "r") as fo:
        formatted = fo.read().format_map(SafeDict(name=proj))
    with open(os.path.join(proj, outpath), "w") as fo:
        fo.write(formatted.strip() + "\n")


def sire(name, mkdocs=False, virtualenv=False):
    """
    Generate a new Python 3.7 project, optionally with a virtualenv and mkthedocs basics
    """
    os.system(f"git init {name}")

    os.makedirs(os.path.join(name, name))
    os.makedirs(os.path.join(name, "tests"))

    paths = [
        "tests/tests.py",
        "requirements.txt",
        "setup.py",
        ".travis.yml",
        f"{name}/__init__.py",
        "CHANGELOG.md",
        "mypy.ini",
        ".bumpversion.cfg",
        ".coveragerc",
        ".gitignore",
        "LICENSE",
        "README.md",
        ".pre-commit-config.yaml",
        "publish.sh",
    ]

    for path in paths:
        write(name, path)

    # make publish executable
    st = os.stat(f"{name}/publish.sh")
    os.chmod(f"{name}/publish.sh", st.st_mode | stat.S_IEXEC)

    # virtualenv stuff
    if virtualenv:
        print("Making virtualenv and installing dependencies")
        os.system(f"python3.7 -m venv {name}/venv-{name}")
        pip = os.path.abspath(f"{name}/venv-{name}/bin/pip")
        os.system(f"{pip} install wheel")
        os.system(f"{pip} install -r {name}/requirements.txt")
        vfile = os.path.join(os.path.dirname(pip), "activate")
        print(f"\n* virtualenv created: activate with `source {vfile}`")

    if not mkdocs:
        print("* Since you're not using mkdocs, please remove RTD badge from README")
        return

    # mkthedocs additions
    os.makedirs(os.path.join(name, "docs"))
    for path in ["mkdocs.yml", "docs/index.md", "docs/about.md"]:
        write(name, path)
    print("* mkdocs generated. Configure readthedocs and a git hook")


if __name__ == "__main__":
    # sorry about the below, i am so lazy
    assert len(sys.argv) > 1, "Please pass in a project name."
    project_name = sys.argv[-1]
    mkdocs = any("mkdocs" in i or "-m" in i for i in sys.argv)
    virtualenv = any("virtualenv" in i or "-v" in i for i in sys.argv)
    try:
        sire(project_name, mkdocs=mkdocs, virtualenv=virtualenv)
    except Exception:
        shutil.rmtree(project_name)
        raise
