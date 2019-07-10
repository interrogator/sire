#!/usr/bin/env python

"""
sire: create a new python3.7 project using all the extra stuff i like.
"""
import argparse
import getpass
import os
import re
import shutil
import stat
import subprocess
import sys
from typing import Any, Mapping

import requests

from .string_matches import BADLINES

GIT_URLS = dict(
    github="https://github.com/{git_username}/{name}",
    bitbucket="https://bitbucket.org/{git_username}/{name}",
    gitlab="https://gitlab.com/{git_username}/{name}",
)

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

# translate between user input for exclude and the pip name, so we can remove
# unused things from requirements
MODULE_TRANSLATION = dict(codecoverage="codecov", bumpversion="bump2version")

# we use these to format help for the user
SHORT_PATHS = [
    os.path.basename(os.path.splitext(i)[0]).strip(".").lower() for i in PATHS
]

# the below just helps with interpreting exclude patterns, so that 'codecov'
# will remove .coveragerc, and so on
EXCLUDE_TRANSLATIONS = dict(
    codecov="coveragerc",
    coverage="coveragerc",
    bump2version="bumpversion",
    rtd="readthedocs",
    readthedocs="readthedocs",
    venv="virtualenv",
    docs="readthedocs",
    test="tests",
)


class SafeDict(dict):
    """
    Need a custom object to not error when formatting files that contain {str}
    """

    def __missing__(self, key):
        return "{" + key + "}"


def _kwargs_to_clean_args(kwargs):
    """
    Add mkdocs, virtualenv and git to exclude set
    """
    exclude = kwargs["exclude"] or str()
    exclude = {EXCLUDE_TRANSLATIONS.get(i, i) for i in exclude.split(",")}
    for special in {"git", "virtualenv", "mkdocs"}:
        if not kwargs[special]:
            print(f"* Skipping {special} because it is in the exclude list.")
            exclude.add(special)
    return kwargs["project_name"], kwargs["git"], kwargs["interactive"], exclude


def _parse_cmdline_args():
    """
    Command line argument parsing. Doing it here means less duplication than
    would be the case in bin/

    Returns tuple of project_name (str), git (str), interactive (bool), exclude (set)
    """
    parser = argparse.ArgumentParser(description="sire a new Python 3.7 project.")
    paths = "/".join(sorted(SHORT_PATHS))

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
        nargs="?",
        type=str,
        required=False,
        choices=["github", "gitlab", "bitbucket"],
        help="Generate .git, .gitignore and hook(s). 'github/bitbucket/gitlab...'",
    )

    parser.add_argument("project_name", help="Name of the new Python project")

    kwargs = vars(parser.parse_args())

    return _kwargs_to_clean_args(kwargs)


def _locate_templates():
    """
    templates dir seems to move around depending on how you install!?

    todo: remove some of these if they are not possible. right now i don't know.
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


def _obtain_git_username(git, name):
    """
    try to figure out the username for a given git remote and project name.
    """
    if git in {"github", "gitlab", "bitbucket"}:
        command = f'ssh -o "StrictHostKeyChecking=no" -T git@{git}.com'
        namefind = r"(?:Hi |logged in as |Welcome to GitLab, @)([a-zA-Z\d]{2,40})"
    else:
        raise NotImplementedError(f"Git host {git} not implemented yet. Make an issue?")

    # first try: see if we can get a good response from our host
    prms: Mapping[str, Any] = dict(
        shell=True, stderr=subprocess.PIPE, universal_newlines=True
    )
    result = subprocess.run(command, **prms)
    match = re.search(namefind, result.stderr)
    if match:
        return match.group(1)
    # otherwise, see if our computer's username exists on the remote...imperfect
    guess = getpass.getuser()
    url = GIT_URLS[git].format(git_username=guess, name=name)
    if requests.get(url).ok:
        return getpass.getuser()
    return False


# directory containing our templates
TEMPLATES = _locate_templates()


def _remove_excluded_lines(formatted, exclude):
    """
    If something is excluded, we don't need it in the readme. Problem is, this
    is a hard thing to automate. So, we just add lots of strings in BADLINES
    """
    out = list()
    for line in formatted.splitlines():
        for ex in exclude:
            badlines = BADLINES.get(ex, list())
            if any(line.startswith(i) for i in badlines):
                break
        else:
            out.append(line)
    return "\n".join(out)


def _write(proj, outpath, formatters, exclude):
    """
    Get the filename from outpath
    read it from templates dir
    format any variables in the templates with projname/other formatters
    write to outpath
    """
    fname = os.path.basename(outpath)
    template = os.path.join(TEMPLATES, fname)
    with open(template, "r") as fo:
        formatted = fo.read().format_map(SafeDict(name=proj, **formatters))
        # hack in some handling of requirements file
        if "requirements" in template:
            deps = {MODULE_TRANSLATION.get(i, i) for i in exclude}
            formatted = "\n".join(i for i in formatted.splitlines() if i not in deps)
        # remove bad lines?
        formatted = _remove_excluded_lines(formatted, exclude)
    with open(os.path.join(proj, outpath.format(name=proj)), "w") as fo:
        fo.write(formatted.strip() + "\n")


def _show_todos(name, paths, exclude, formatters, git):
    """
    Make a formatted str of things to do from here. Mostly so the user can copy
    urls and so on (to quickly set up hooks, git remote)
    """
    todos = [f"Actually write some tests: {name}/tests.py"]
    if ".coveragerc" in paths:
        todos.append("Set up codecov and a git hook for it.")
    if "mkdocs" not in exclude:
        rtd = "https://readthedocs.org/dashboard/import"
        todos.append(f"Set up a readthedocs and a git hook for it: {rtd}")
    if "git" not in exclude:
        git_username = formatters.get("git_username", "<username>")
        git_url = GIT_URLS[git].format(git_username=git_username, name=name)
        add_remote = f"git remote add origin {git_url}"
        set_remote = f"git remote set-url origin {git_url}"
        os.chdir(name)
        subprocess.call(add_remote.split())
        print(f"Added remote 'origin': {git_url}")
        subprocess.call(set_remote.split())
        print(f"Set remote: {git_url}")
        os.chdir("..")
    form = "\n* ".join(todos)
    # right now, there is always at least one todo note (do tests!)
    cd = f"`cd {name}`"
    print(f"\nAll done! {cd} to check out your new project.\n\nTo do:\n\n* {form}")


def _filter_excluded(exclude):
    """
    Get just the subset of PATH strings that we need to process, based on the
    contents of exclude, which was already pre-processed during argument parsing
    """
    if not exclude:
        return PATHS

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
    """
    Run input() with formatted prompt, and return
    The while loop can be used to ensure correct output
    """
    while True:  # while input not understood
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
        print("Error: answer not understood. You can 'quit' or hit ctrl+c to exit.")


def _interactive(git, name):
    """
    Interactive assistant. This will supercede any command line arguments, meaning
    that it is pointless to add any other arguments when using the -i argument.
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
    # attempt to get some variables from shell. not sure how this looks when absent
    usr = _obtain_git_username(git, name)
    email = "git config user.email".split()
    email = subprocess.check_output(email).decode("utf-8").strip()
    real_name = "git config user.name".split()
    real_name = subprocess.check_output(real_name).decode("utf-8").strip()
    short = "/".join(sorted(SHORT_PATHS))
    exes = f"Comma separated list of files to exclude\n(e.g. {short}):  "

    # tuples are field name, prompt text, default
    prompts = [
        ("real_name", "Real name (for license, setup.py) ({default}):  ", real_name),
        ("username", "Username ({default}):  ", usr),
        ("email", "Email ({default}):  ", email),
        ("git_username", "GitHub/GitLab/Bitbucket username ({default}):  ", usr),
        ("description", "Short project description:  ", None),
        # ("license", "Licence to use ({default}):  ", "MIT"),
        ("mkdocs", "Use mkdocs/readthedocs for documentation (y/N):  ", False),
        ("virtualenv", "Generate a virtualenv for this project (y/N):  ", False),
        ("git", "Git host to use (github,gitlab,bitbucket/None):  ", None),
        ("exclude", exes, set()),
    ]

    for field, prompt, default in prompts:
        output[field] = _input_wrap(prompt, default)
    return output.pop("git"), output


def sire(name, git=None, interactive=False, exclude=None):
    """
    Generate a new Python 3.7 project, optionally with .git, virtualenv and
    mkthedocs basics present too.
    """
    git, formatters = git, dict() if not interactive else _interactive(git, name)

    # print abspath because user might want it for copying...
    dirname = os.path.abspath(f"./{name}")
    print(f"\nGenerating new project at `{dirname}`...")

    # make module and test dirs. i'm not making it possible to avoid tests!
    os.makedirs(os.path.join(name, name))
    with open(os.path.join(name, name, name + ".py"), "w") as fo:
        fo.write("")
    os.makedirs(os.path.join(name, "tests"))
    with open(os.path.join(name, "tests", "__init__.py"), "w") as fo:
        fo.write("")

    # get set of paths minus what is in exclude
    paths = _filter_excluded(exclude)

    # add git extras if the user wants
    if "git" not in exclude:
        subprocess.call(f"git init {name}".split())
        paths.update({".gitignore", ".pre-commit-config.yaml"})
        formatters["git_username"] = _obtain_git_username(git, name)

    # mkdocs extras
    if "mkdocs" not in exclude:
        files = {"mkdocs.yml", "docs/index.md", "docs/about.md", ".readthedocs.yaml"}
        os.makedirs(os.path.join(name, "docs"))
        paths.update(files)

    # format and copy over the paths
    for path in paths:
        _write(name, path, formatters, exclude)

    # make publish executable
    st = os.stat(f"{name}/publish.sh")
    os.chmod(f"{name}/publish.sh", st.st_mode | stat.S_IEXEC)

    # virtualenv creation and requirements install
    if "virtualenv" not in exclude:
        _build_virtualenv(name)

    # print todos, so that the user can quickly copy and paste urls etc.
    _show_todos(name, paths, exclude, formatters, git)


def wrapped_sire(*args):
    """
    Make sure that the directory is deleted if there is an error during sire
    """
    try:
        sire(*args)
    except KeyboardInterrupt:
        print("Process stopped by user. Aborting and cleaning up ...")
        shutil.rmtree(args[0], ignore_errors=True)
    except Exception:
        print("Error during project creation. Aborting and cleaning up ...")
        shutil.rmtree(args[0], ignore_errors=True)
        raise


if __name__ == "__main__":
    wrapped_sire(*_parse_cmdline_args())
