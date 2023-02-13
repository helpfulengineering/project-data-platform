from pathlib import Path

import typer

from .parser import Okh
from .utils import console

# create the app
cli = typer.Typer(pretty_exceptions_show_locals=False)


@cli.command()
def version():
    console.print("0.1.0")


@cli.command()
def parse(source: str, destination: str = None):
    """run the app in the current directory.

    Args:
        source: file to be parsed.
        destination: dir to store parsed file.
    """
    if destination and Path(destination).is_file():
        console.print("[red][bold] destination directory cannot be a file")
        typer.Exit()

    okh_object = Okh(Path(source), Path(destination))
    okh_object.parse_file()
    okh_object.save()


main = cli

if __name__ == "__main__":
    main()
