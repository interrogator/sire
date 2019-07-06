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

PATHS = {
    ".bumpversion.cfg",
    ".coveragerc",
    ".flake8",
    ".travis.yml",
    "CHANGELOG.md",
    "LICENSE",
    "mypy.ini",
    "publish.sh",
    "README.md",
    "requirements.txt",
    "setup.py",
    "tests/tests.py",
    "{name}/__init__.py",
}

# the below just helps with interpreting exclude patterns, so that 'codecov'
# will remove .coveragerc, and so on
EXCLUDE_TRANSLATIONS = dict(
    codecov="coveragerc",
    coverage="coveragerc",
    bump2version="bumpversion.cfg",
    test="tests.py",
)


def _parse_cmdline_args():

    parser = argparse.ArgumentParser(description="sire a new Python 3.7 project.")
    extra = [os.path.basename(os.path.splitext(i)[0]).strip(".").lower() for i in PATHS]
    paths = "/".join(sorted(extra))

    parser.add_argument(
        "-e",
        "--exclude",
        nargs="?",
        type=str,
        required=False,
        help=f"Comma separated files/modules to exclude. Any of: {paths}",
    )

    parser.add_argument(
        "-m",
        "--mkdocs",
        default=False,
        action="store_true",
        required=False,
        help="Generate files for mkdocs/readthedocs",
    )

    parser.add_argument(
        "-v",
        "--virtualenv",
        default=False,
        action="store_true",
        required=False,
        help="Generate a virtualenv for this project",
    )

    parser.add_argument(
        "-g",
        "--git",
        default=False,
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
    with open(os.path.join(proj, outpath.format(name=proj)), "w") as fo:
        fo.write(formatted.strip() + "\n")


def _make_todos(name, paths, mkdocs, git):
    """
    Make a formatted list of things to do from here
    """
    todos = [f"Actually write some tests: {name}/tests.py"]
    if ".coveragerc" in paths:
        todos.append("Set up codecov and a git hook for it.")
    if mkdocs:
        todos.append("Set up a readthedocs and a git hook for it.")
    if git:
        url = f"git remote set-url origin https://github.com/<user>/{name}"
        todos.append(f"Set git remote: (e.g.) {url}")
    return "\n* ".join(todos)


def _filter_excluded(exclude, **kwargs):
    """
    Remove files the user does not want to generate...
    """
    filtered = set()
    trans_exclude = set()
    exclude = {i.strip().lower().lstrip(".") for i in exclude.split(",")}
    trans_exclude = {EXCLUDE_TRANSLATIONS.get(i, i) for i in exclude}
    for name in kwargs:
        if name in trans_exclude:
            print(f"* Skipping {name} because it is in the exclude list.")
            kwargs[name] = False
    # annoyingly, this could be a one-liner, but for print and so on we can't
    for path in PATHS:
        no_pth = os.path.basename(path).lstrip(".")
        no_ext = os.path.splitext(no_pth)[0]
        if no_pth.lower() in trans_exclude or no_ext.lower() in trans_exclude:
            print(f"* Skipping {path} because it is in the exclude list.")
            continue
        filtered.add(path)
    return filtered, kwargs["mkdocs"], kwargs["virtualenv"], kwargs["git"]


def sire(name, mkdocs=True, virtualenv=True, git=True, exclude=None):
    """
    Generate a new Python 3.7 project, optionally with .git, virtualenv and
    mkthedocs basics present too.
    """
    dirname = os.path.abspath(f"./{name}")
    print(f"\nGenerating new project at `{dirname}`...")
    # remove things specific in includes
    # also, if the user does exclude=mkdocs/virtualenv, flag these
    if exclude:
        extra = dict(mkdocs=mkdocs, virtualenv=virtualenv, git=git)
        paths, mkdocs, virtualenv, git = _filter_excluded(exclude, **extra)
    else:
        paths = PATHS

    # add git extras if the user wants
    if git:
        subprocess.call(f"git init {name}".split())
        paths.update({".gitignore", ".pre-commit-config.yaml"})

    # make module and test dirs
    os.makedirs(os.path.join(name, name))
    os.makedirs(os.path.join(name, "tests"))

    # mkdocs extras
    if mkdocs:
        os.makedirs(os.path.join(name, "docs"))
        paths.update(
            {"mkdocs.yml", "docs/index.md", "docs/about.md", ".readthedocs.yaml"}
        )

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

    todos = _make_todos(name, paths, mkdocs, git)

    print(
        f"\nAll done! `cd {name}` to check out your new project."
        f"\n\nTo do:\n\n* {todos}\n"
    )


def wrapped_sire(**kwargs):
    """
    Make sure that the directory is deleted if there is an error during sire
    """
    try:
        sire(**kwargs)
    except KeyboardInterrupt:
        print("Process stopped by user. Aborting and cleaning up ...")
        shutil.rmtree(kwargs["name"], ignore_errors=True)
    except Exception:
        print("Error during project creation. Aborting and cleaning up ...")
        shutil.rmtree(kwargs["name"], ignore_errors=True)
        raise


if __name__ == "__main__":
    wrapped_sire(**_parse_cmdline_args())
