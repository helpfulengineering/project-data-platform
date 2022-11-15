# project-data
An experimental attempt to make a CLI for supply-chain modeling for Helpful Engineering's Project Data

# Installation and running

Installation requires four parts:

1. Installation of Python3.8 or greater, *(left as an exercise to reader.)*
2. Installation of a Python package manager.
  - We use and recommend [Poetry](https://python-poetry.org).
  - Alternatively, `pip` or `conda` will suffice.
3. Installation of the `okf-library` through `git submodule update`

## Installation and running with Poetry (recommended):

This project uses `poetry`, an MIT licensed packaging-manager and dependency-manager. Poetry can be installed on **MacOS, Linux, or WSL** as follows:

`curl -sSL https://install.python-poetry.org | python3 -`

If you receive a `command not found: python3` error, you may need to replace `python3` with `py` or `python`.

**Windows users** can install Poetry through Powershell as follows:

`(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`

In the case of an error, replace `py` with `python3` or `python`.



Also, we use a submodule, you may have to execute:

> git submodule update

# Process

As part of our attempt to make a usable matching process, we plan to implement the following process:

![Diagram of OKF Document Processing Workflow](https://user-images.githubusercontent.com/5296671/199362652-e490d2d4-d191-424e-859c-3a81fe94eca8.png)
