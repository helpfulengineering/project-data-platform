from pathlib import Path

import typer
import yaml

from tools.okparser.src import utils

__REQUIRED_FIELDS__ = frozenset({"bom", "tool-list"})


class Okh:
    # list of bom atoms with wiki data
    bom_atoms: list[dict[str, str]]
    # list of tools with wikidata
    tool_list_atoms: list[dict[str, str]]
    # extracted yaml content
    yaml_content: dict

    def __init__(self, source_path: Path):
        """Initialize class and generate okh

        Args:
            source_path:  path to file to source file.
        """
        self.generate_okh(source_path)

    @staticmethod
    def open(source_path: Path):
        """open the source file and generate okh.

        Args:
            source_path: path to file to process.

        Returns:
            okh instance.
        """
        return Okh(source_path)

    def bom_atoms_exists(self):
        """check if bom atoms exists."""

        return self.yaml_content.get("bom-atoms") is not None

    def tool_list_atoms_exist(self):
        """check if tool list atoms exists."""
        return self.yaml_content.get("tool-list-atoms") is not None

    def generate_okh(self, source_path) -> None:
        """Parse a yaml file and obtain wikidata for boms and tool-lists

        Args:
            source_path: file to process

        """
        self.yaml_content = utils.read_yaml_file(source_path)

        if self.bom_atoms_exists() and self.tool_list_atoms_exist():
            typer.Exit()
        if not self.bom_atoms_exists():
            bom_items = self.yaml_content.get("bom", "").split(",")
            self.bom_atoms = utils.get_wiki_data(bom_items)

        if not self.tool_list_atoms_exist():
            tool_list = self.yaml_content.get("tool-list", "").split(",")
            self.tool_list_atoms = utils.get_wiki_data(tool_list)

    def save(self, destination_path: Path) -> None:
        """save newly generated yaml contents into a file.

        Args:
            destination_path: where to save file.
        """
        yaml_content = (
            self.yaml_content
            | {"bom-atoms": self.bom_atoms}
            | {"tool-list-atoms": self.tool_list_atoms}
        )
        if yaml_content:
            with open(
                destination_path,
                "w",
            ) as yaml_file:
                yaml.dump(
                    yaml_content, yaml_file, default_flow_style=False, sort_keys=False
                )
            utils.console.print(
                f"[green][bold]yaml file generated at {destination_path}"
            )
