# project-data
An experimental attempt to make a CLI for supply-chain modeling for Helpful Engineering's Project Data



# Installation and running

Installation requires four parts:

1. Clone this repository with `git@github.com:helpfulengineering/project-data-platform.git --recursive`
  - If cloned without, 
2. Installation of Python3.8 or greater, *(left as an exercise to reader.)*
3. Installation of the Poetry Python package-manager and build-tool.
  - We use and recommend [Poetry](https://python-poetry.org).
  - Alternatively, `pip` or `conda` can be used.
4. Installation of the `okf-library` through `git submodule update`


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

This project uses `poetry`, an MIT licensed packaging-manager and dependency-manager.

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

## Installing and running without Poetry. (

Check `poetry.lock` for the version numbers of dependencies we use, `yamale` or `sympy`.


## Running with Poetry (recommended): (TODO)




# Process

As part of our attempt to make a usable matching process, we plan to implement the following process:

![Diagram of OKF Document Processing Workflow](https://user-images.githubusercontent.com/5296671/199362652-e490d2d4-d191-424e-859c-3a81fe94eca8.png)

(TODO from here down)