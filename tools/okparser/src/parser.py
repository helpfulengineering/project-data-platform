import re
from pathlib import Path

import requests
import typer
import yaml

from tools.okparser.src import utils

__REQUIRED_FIELDS__ = frozenset({"bom", "tool-list"})


def get_wiki_data(items: list[str]) -> list[dict[str, str]]:
    """search the wikidata api for items.

    Args:
        items: list of items(bom items, tools) to be searched.
    Returns:
        A list of search descriptions for each item.
    """
    item_list = []
    with typer.progressbar(items, color=True) as progress:
        for item in progress:
            item_dict = {"identifier": "", "description": item.strip(), "link": ""}
            # look for 'or' keyword in text and search each item
            sub_items = item.split("or")
            for sub_item in sub_items:
                response = requests.get(utils.get_url(sub_item)).json()
                if response["search"]:
                    # get the first result from the search results for now
                    item_dict["identifier"] = response["search"][0]["id"]
                    item_dict["link"] = re.sub(
                        "//www.", "https://", response["search"][0]["url"]
                    )
                    break
                utils.console.print(f"\t[red]couldn't find wikidata for {sub_item}")
            item_list.append(item_dict)
    return item_list


class Okh:
    # list of bom atoms with wiki data
    bom_atoms: list[dict[str, str]]
    # list of tools with wikidata
    tool_list_atoms: list[dict[str, str]]
    # source_path of yaml file
    source_path: Path
    # destination_path of yaml file
    destination_path: Path
    # extracted yaml content
    yaml_content: dict

    def __init__(self, source_path: Path, destination_path: Path):
        self.source_path = source_path
        self.destination_path = destination_path

    def parse_file(self) -> None:
        """Parse a yaml file and obtain wikidata for boms and tool-lists"""
        self.yaml_content = utils.read_yaml_file(self.source_path)

        bom_items = self.yaml_content.get("bom", "").split(",")

        tool_list = self.yaml_content.get("tool-list", "").split(",")

        self.bom_atoms = get_wiki_data(bom_items)
        self.tool_list_atoms = get_wiki_data(tool_list)

    def save(self) -> None:
        """save newly generated yaml contents into a file"""
        yaml_content = (
            self.yaml_content
            | {"bom-atoms": self.bom_atoms}
            | {"tool-list-atoms": self.tool_list_atoms}
        )
        if yaml_content:
            with open(
                self.destination_path / utils.generate_file_name(self.source_path.name),
                "w",
            ) as yaml_file:
                yaml.dump(
                    yaml_content, yaml_file, default_flow_style=False, sort_keys=False
                )
            utils.console.print(
                f"[green][bold]yaml file generated at {self.source_path.parent}"
            )
