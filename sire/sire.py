#!/usr/bin/env python

"""
sire: create a new python3.7 project using all the extra stuff i like.
"""
import argparse
import getpass
import os
import shutil
import stat
import subprocess
import sys
from collections import OrderedDict

# here we store the out paths that will be generated. not included are git and
# mkdocs-related files, as they are added in later if the user requests them
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
    rtd="readthedocs.cfg",
    readthedocs="readthedocs.cfg",
    venv="virtualenv",
    docs="readthedocs.cfg",
    test="tests.py",
)


class SafeDict(dict):
    """
    Need a custom object to not error when formatting files that contain {str}
    """

    def __missing__(self, key):
        return "{" + key + "}"


def _clean_kwargs(kwargs):
    """
    Turn exclude into a set of normalised strings, and translate
    exclude=git,virtualenv to git=False, virtualenv=False etc
    """
    exclude = kwargs["exclude"]
    if not exclude:
        return kwargs
    exclude = {EXCLUDE_TRANSLATIONS.get(i, i) for i in exclude.split(",")}
    for special in {"git", "virtualenv", "mkdocs"}:
        if special in exclude:
            print(f"* Skipping {special} because it is in the exclude list.")
            kwargs[special] = False
    kwargs["exclude"] = exclude
    return kwargs


def _parse_cmdline_args():
    """
    Command line argument parsing. Doing it here means less duplication than
    would be the case in bin/
    """

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
        "-i",
        "--interactive",
        default=False,
        action="store_true",
        required=False,
        help="Interactive prompt with a few extra fields to autofill",
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

    parser.add_argument("project_name", help="Name of the new Python project")

    kwargs = vars(parser.parse_args())
    kwargs["name"] = kwargs.pop("project_name")

    return _clean_kwargs(kwargs)


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


def _write(proj, outpath, formatters):
    """
    Get the filename from outpath
    read it from templates dir
    add project name to anywhere {name} appears in doc
    write to outpath
    """
    fname = os.path.basename(outpath)
    template = os.path.join(TEMPLATES, fname)
    with open(template, "r") as fo:
        formatted = fo.read().format_map(SafeDict(name=proj, **formatters))
    with open(os.path.join(proj, outpath.format(name=proj)), "w") as fo:
        fo.write(formatted.strip() + "\n")


def _make_todos(name, paths, mkdocs, git, github_username):
    """
    Make a formatted str of things to do from here. Mostly so the user can copy
    """
    todos = [f"Actually write some tests: {name}/tests.py"]
    if ".coveragerc" in paths:
        todos.append("Set up codecov and a git hook for it.")
    if mkdocs:
        rtd = "https://readthedocs.org/dashboard/import"
        todos.append(f"Set up a readthedocs and a git hook for it: {rtd}")
    if git:
        url = f"git remote set-url origin https://github.com/{github_username}/{name}"
        todos.append(f"Set git remote: (e.g.) {url}")
    return "\n* ".join(todos)


def _filter_excluded(exclude):
    """
    Get just the subset of PATH strings that we need to process, based on the
    contents of exclude, which was already pre-processed during argument parsing
    """
    if not exclude:
        return PATHS

    # return a subset of PATHS based on exclude
    filtered = set()
    for path in PATHS:
        # remove path and extension from
        no_pth = os.path.basename(path).lstrip(".")
        no_ext = os.path.splitext(no_pth)[0]
        possible = {path, no_pth, no_ext}
        if any(i in exclude for i in possible):
            print(f"* Skipping {path} because it is in the exclude list.")
            continue
        filtered.add(path)
    return filtered


def _build_virtualenv(name):
    """
    If the user wants, make a new virtualenv, install dependencies, and
    print some helpful copyable strings along the way
    """
    print("Making virtualenv and installing dependencies")
    subprocess.call(f"python3.7 -m venv {name}/venv-{name}".split())
    pip = os.path.abspath(f"{name}/venv-{name}/bin/pip")
    subprocess.call(f"{pip} install wheel".split())
    subprocess.call(f"{pip} install -r {name}/requirements.txt".split())
    vfile = os.path.join(os.path.dirname(pip), "activate")
    print(f"\n* virtualenv created: activate with `source {vfile}`")


def _input_wrap(prompt, default=None):
    understood = False
    while not understood:
        result = input(prompt.format(default=default)).lower().strip()
        if result in {"y", "yes"}:
            return True
        if result in {"n", "no"}:
            return False
        if not result:
            return default
        if result in {"quit", "q", "exit"}:
            raise RuntimeError("User quit.")
        if not isinstance(default, bool):
            return result
        print("Error: answer not understood")


def _interactive(name, **kwargs):
    """
    Interactive assistant
    """
    prompt = (
        "\n========================================================================\n"
        "This is the interactive helper for *sire*. Details entered here will \n"
        "determine which files are included, and format them with the correct \n"
        "information. Leaving a field blank is OK, but can result in incompletely \n"
        "formatted files. Hit enter to begin, or type 'quit' to quit.\n"
        "========================================================================\n\n"
    )
    _input_wrap(prompt)
    output = dict()

    usr = getpass.getuser()
    email = "git config user.email".split()
    email = subprocess.check_output(email).decode("utf-8").strip()
    real_name = "git config user.name".split()
    real_name = subprocess.check_output(real_name).decode("utf-8").strip()
    exes = "Comma separated list of files to exclude (e.g. travis/mypy/bumpversion):  "

    prompts = OrderedDict(
        real_name=("Real name (for license, setup.py) ({default}):  ", real_name),
        username=("Username ({default}):  ", usr),
        email=("Email ({default}):  ", email),
        github_username=("GitHub username ({default}):  ", usr),
        description=("Short project description:  ", None),
        # license=("Licence to use: ({default})", "MIT"),
        mkdocs=("Use mkdocs/readthedocs for documentation (y/N):  ", False),
        virtualenv=("Generate a virtualenv for this project (y/N):  ", False),
        git=("Initialise as a git repo (y/N):  ", False),
        exclude=(exes, set()),
    )

    for field, (prompt, default) in prompts.items():
        output[field] = _input_wrap(prompt, default)
    return output


def sire(name, mkdocs=True, virtualenv=True, git=True, exclude=None, interactive=False):
    """
    Generate a new Python 3.7 project, optionally with .git, virtualenv and
    mkthedocs basics present too.
    """
    kwargs = dict(mkdocs=mkdocs, virtualenv=virtualenv, git=git, exclude=exclude)
    formatters = dict() if not interactive else _interactive(name, **kwargs)
    if interactive:
        mkdocs, virtualenv, git, exclude = (
            formatters.pop("mkdocs"),
            formatters.pop("virtualenv"),
            formatters.pop("git"),
            formatters.pop("exclude"),
        )

    # print abspath because user might want it for copying...
    dirname = os.path.abspath(f"./{name}")
    print(f"\nGenerating new project at `{dirname}`...")

    # make module and test dirs. i'm not making it possible to avoid tests!
    os.makedirs(os.path.join(name, name))
    os.makedirs(os.path.join(name, "tests"))

    # get set of paths minus what is in exclude
    paths = _filter_excluded(exclude)

    # add git extras if the user wants
    if git:
        subprocess.call(f"git init {name}".split())
        paths.update({".gitignore", ".pre-commit-config.yaml"})

    # mkdocs extras
    if mkdocs:
        files = {"mkdocs.yml", "docs/index.md", "docs/about.md", ".readthedocs.yaml"}
        os.makedirs(os.path.join(name, "docs"))
        paths.update(files)

    # format and copy over the paths
    for path in paths:
        _write(name, path, formatters)

    # make publish executable
    st = os.stat(f"{name}/publish.sh")
    os.chmod(f"{name}/publish.sh", st.st_mode | stat.S_IEXEC)

    if virtualenv:
        _build_virtualenv(name)

    gh_username = formatters.get("github_username", "<username>")
    todos = _make_todos(name, paths, mkdocs, git, gh_username)

    final = f"\nAll done! `cd {name}` to check out your new project."
    if todos:
        final += f"\n\nTo do:\n\n* {todos}\n"
    print(final)


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
