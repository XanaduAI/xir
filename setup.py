from setuptools import setup, find_packages
import re

with open("xir/_version.py") as f:
    version = f.readlines()[-1].split()[-1].strip("\"'")

requirements = ["lark-parser>=0.11.0"]

info = {
    "description": "XIR is an intermediate representation (IR) for quantum circuits.",
    "include_package_data": True,
    "install_requires": requirements,
    "license": "Apache License 2.0",
    "license_files": ["LICENSE"],
    "long_description_content_type": "text/markdown",
    "long_description": open("README.md").read(),
    "maintainer_email": "software@xanadu.ai",
    "maintainer": "Xanadu Inc.",
    "name": "quantum-xir",
    "package_data": {"xir": ["xir.lark"]},
    "packages": find_packages(where="."),
    "provides": ["xir"],
    "url": "https://github.com/XanaduAI/xir",
    "version": version,
}

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Scientific/Engineering :: Physics",
]

setup(classifiers=classifiers, **(info))
