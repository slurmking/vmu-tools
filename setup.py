"""Install packages as defined in this file into the Python environment."""
import pathlib
from setuptools import setup, find_packages

# The version of this tool is based on the following steps:
# https://packaging.python.org/guides/single-sourcing-package-version/


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="vmu_tools",
    author="slurmking",
    url="https://github.com/slurmking/vmu-tools",
    description="A set of tools for Dreamcast VMU icon",
    long_description=README,
    long_description_content_type='text/markdown',
    version="0.1.4",
    packages=find_packages(include=['vmut', 'vmut.*']),
    install_requires=[
        "Pillow",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
