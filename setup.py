#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
import toml
import json
from setuptools import setup, find_packages


def get_from_pipfile(section):
    """Load up the requirements from the Pipfile"""
    if section not in ["packages", "dev-packages"]:
        raise "You must choose a valid section"

    try:
        with open("Pipfile", "r") as f:
            pipfile = f.read()
        parsed = toml.loads(pipfile)

    except FileNotFoundError:
        return []

    try:
        packages = parsed[section].items()
    except KeyError:
        return []

    def format_package(package, version):
        if type(version) == dict:
            print(version.items())
            version = version["version"]

        if version == "*":
            return package
        else:
            return f"{package}{version}"

    return [
        format_package(package, version) if version != "*" else package
        for package, version in packages
    ]


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()
CHANGES = open(os.path.join(here, "CHANGES.md")).read()

about = {}
with open(os.path.join(here, "thunderbird", "__version__.py"), "r") as f:
    exec(f.read(), about)

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Scientific/Engineering :: Atmospheric Science",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
]

setup(
    name="thunderbird-daccs",
    version=about["__version__"],
    description="A Web Processing Service for Climate Explorer data preparation",
    long_description=README + "\n\n" + CHANGES,
    author=about["__author__"],
    author_email=about["__email__"],
    url="https://github.com/pacificclimate/thunderbird",
    classifiers=classifiers,
    license="GNU General Public License v3",
    keywords="wps pywps birdhouse thunderbird",
    packages=find_packages(),
    package_data={
        "thunderbird": ["tests/data/*.nc", "tests/metadata-conversion/*.yaml"],
        "tests": ["data/*.nc", "metadata-conversion/*.yaml"],
    },
    include_package_data=True,
    install_requires=get_from_pipfile("packages"),
    extras_require={"dev": get_from_pipfile("dev-packages")},
    entry_points={"console_scripts": ["thunderbird=thunderbird.cli:cli"]},
)
