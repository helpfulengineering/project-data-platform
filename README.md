# project-data

An experimental attempt to make a CLI for supply-chain modeling for Helpful Engineering's Project Data

Click here to view the [SCIS pilot project early code walk through video](https://youtu.be/IAYBdHfAjxg).


# Installation and running

First, clone the library and add the submodule:

```
# Clone library
git clone git@github.com:helpfulengineering/project-data-platform.git --recursive
# Alternatively, uncomment to clone with HTTPS:
# https://github.com/helpfulengineering/project-data-platform.git --recursive

cd project-data-platform

# If the submodule does not appear, explicitly add it:
# git submodule add git@github.com:helpfulengineering/library.git ./okf-library

# Install Python 3 -- left as an exercise to reader
# Install Poetry and dependencies -- see below
```

## Installation and running with Poetry (recommended):

> **tldr:**
> 
> ```
> curl -sSL https://install.python-poetry.org | python3 -
> git submodule update
> poetry install
> poetry run python src/helloworld.py
> ```
>
> Poetry might look like overkill, but will be massively useful for saving time.

This project uses [`poetry`, an MIT licensed packaging-manager and dependency-manager.](https://python-poetry.org/

**Users on MacOS, Linux, WSL, or Unix-likes**  can install Poetry as follows:

`curl -sSL https://install.python-poetry.org | python3 -`

**Users on Windows** can install Poetry through Powershell as follows:

`(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`

**In the case of an error**, your Python installation might point to `python3`, `py`, or `python`.

You can check Poetry is installed with the command `poetry -h`. Poetry has [basic usage documentation](https://python-poetry.org/docs/basic-usage/) and is recommended reading.

After installing Poetry, install the `okf-library` as follows:

`git submodule update`

Then, the dependencies (described in `poetry.lock`) can be installed as follows:

`poetry install`

Finally, run code as follows:

`poetry run python src/helloworld.py`

## Installing and running without Poetry.

Check `pyproject.toml` for the most up-to-date version numbers of dependencies we use, `yamale` or `sympy`.

As of this README, that's Python 3.10, Yamale 4.0.4, and Sympy 1.11.1.


# Using Jupyter notebooks

The `notebooks` folder contains a code demo. These `.ipynb` are called "Jupyter Notebooks". [Install Jupyter Lab for your machine to work with notebooks](https://jupyter.org/install), or install a Jupyter Notebook  extension (such as [for VSCode](https://devblogs.microsoft.com/python/introducing-the-jupyter-extension-for-vs-code/), or [for emacs](https://github.com/nnicandro/emacs-jupyter), or try using [Jupyter running in your browser](https://jupyter.org/try-jupyter/lab/).


# Process description

As part of our attempt to make a usable matching process, we plan to implement the following process:

![Diagram of OKF Document Processing Workflow (3)](docs/ProcessDescription.png)

# Internal Workflow

This team has decided to work in branches, and to have at least one other person review code before it is merged into main.
