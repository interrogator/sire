#!/usr/bin/env python

"""
sire: create a new python3.7 project using all the extra stuff i like.
"""

import argparse
import os
import shutil
import stat
import subprocess
import sys


def _parse_cmdline_args():

    parser = argparse.ArgumentParser(description="sire a new Python 3.7 project.")

    parser.add_argument(
        "-e",
        "--exclude",
        nargs="?",
        type=str,
        required=False,
        help="Comma separated files/modules to exclude (travis,mypy,__init__...)",
    )

    parser.add_argument(
        "-m",
        "--mkdocs",
        default=True,
        action="store_true",
        required=False,
        help="Generate files for mkdocs/readthedocs",
    )

    parser.add_argument(
        "-v",
        "--virtualenv",
        default=True,
        action="store_true",
        required=False,
        help="Generate a virtualenv for this project",
    )

    parser.add_argument(
        "-g",
        "--git",
        default=True,
        action="store_true",
        required=False,
        help="Generate .git, .gitignore and hook(s)",
    )

    parser.add_argument("name", help="Name of the new Python project")

    return vars(parser.parse_args())


def _locate_templates():
    """
    templates dir seems to move around depending on how you install!?
    """
    fpath = os.path.dirname(__file__)
    first = os.path.dirname(fpath)
    second = os.path.dirname(first)
    third = sys.prefix
    fourth = os.path.join(third, "sire")
    dirs = [first, second, third, fourth]
    for path in dirs:
        if os.path.isdir(os.path.join(path, "templates")):
            return os.path.join(path, "templates")
    raise ValueError(f"No templates found in: {dirs}")


TEMPLATES = _locate_templates()


class SafeDict(dict):
    """
    Need a custom object to not error when formatting files that contain {var}
    """

    def __missing__(self, key):
        return "{" + key + "}"


def _write(proj, outpath):
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


def _filter_excluded(paths, exclude, mkdocs, virtualenv):
    """
    Remove files the user does not want to generate...
    """
    filtered = list()
    exclude = [i.strip().lower() for i in exclude.split(",")]
    if "mkdocs" in exclude:
        print(f"* Skipping mkdocs/readthedocs because it is in the exclude list.")
        mkdocs = False
    if "virtualenv" in exclude:
        print(f"* Skipping virtualenv creation because it is in the exclude list.")
        virtualenv = False
    # annoyingly, this could be a one-liner, but for print and so on we can't
    for path in paths:
        no_pth = os.path.basename(path)
        no_ext = os.path.splitext(no_pth)[0]
        if no_pth.lower() in exclude or no_ext.lower() in exclude:
            print(f"* Skipping {path} because it is in the exclude list.")
            continue
        filtered.append(path)
    return filtered, mkdocs, virtualenv


def sire(name, mkdocs=True, virtualenv=True, git=True, exclude=None):
    """
    Generate a new Python 3.7 project with .git, and
    optionally with a virtualenv and mkthedocs basics
    """
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
        "LICENSE",
        "README.md",
        "publish.sh",
    ]

    # remove things specific in includes
    # also, if the user does exclude=mkdocs/virtualenv, flag these
    if exclude:
        paths, mkdocs, virtualenv = _filter_excluded(paths, exclude, mkdocs, virtualenv)

    # add git extras if the user wants
    if git:
        subprocess.call(f"git init {name}".split())
        paths += [".gitignore", ".pre-commit-config.yaml"]

    # make module and test dirs
    os.makedirs(os.path.join(name, name))
    os.makedirs(os.path.join(name, "tests"))

    # mkdocs extras
    if mkdocs:
        os.makedirs(os.path.join(name, "docs"))
        paths += ["mkdocs.yml", "docs/index.md", "docs/about.md", ".readthedocs.yaml"]

    # format and copy over the paths
    for path in paths:
        _write(name, path)

    # make publish executable
    st = os.stat(f"{name}/publish.sh")
    os.chmod(f"{name}/publish.sh", st.st_mode | stat.S_IEXEC)

    # virtualenv stuff
    if virtualenv:
        print("Making virtualenv and installing dependencies")
        subprocess.call(f"python3.7 -m venv {name}/venv-{name}".split())
        pip = os.path.abspath(f"{name}/venv-{name}/bin/pip")
        subprocess.call(f"{pip} install wheel".split())
        subprocess.call(f"{pip} install -r {name}/requirements.txt".split())
        vfile = os.path.join(os.path.dirname(pip), "activate")
        print(f"\n* virtualenv created: activate with `source {vfile}`")

    print(f"All done! `cd {name}` to check out your new project.")


def wrapped_sire(**kwargs):
    """
    Make sure that the directory is deleted if there is an error during sire
    """
    try:
        sire(**kwargs)
    except KeyboardInterrupt:
        print("Process stopped by user. Aborting and cleaning up ...")
        shutil.rmtree(kwargs["name"])
    except Exception:
        print("Error during project creation. Aborting and cleaning up ...")
        shutil.rmtree(kwargs["name"])
        raise


if __name__ == "__main__":
    wrapped_sire(**_parse_cmdline_args())
