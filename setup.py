import os

from setuptools import setup


def read(fname):
    """
    Helper to read README
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()


data_files = [
    f"templates/{i}"
    for i in os.listdir("templates")
    if os.path.isfile(f"templates/{i}")
]

setup(
    name="sire",
    version="1.0.0",
    description="Python project generator",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="http://github.com/interrogator/sire",
    author="Danny McDonald",
    include_package_data=True,
    zip_safe=False,
    packages=["sire"],
    data_files=[("templates", data_files)],
    scripts=["bin/sire"],
    author_email="mcddjx@gmail.com",
    license="MIT",
    keywords=[],
    install_requires=[],
    dependency_links=[],
)
