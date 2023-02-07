from pathlib import Path

import typer

from .parser import Okh
from .utils import console

# create the app
cli = typer.Typer(pretty_exceptions_show_locals=False)


@cli.command()
def version():
    console.print(version)


@cli.command()
def parse(path: str):
    """run the app in the current directory."""

    okh_object = Okh(Path(path))
    okh_object.parse_file()
    okh_object.save()


main = cli

if __name__ == "__main__":
    main()
