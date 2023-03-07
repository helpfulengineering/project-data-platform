import re
from pathlib import Path

import requests
import typer
import yaml
from rich.console import Console

# Console for pretty printing.
console = Console()


def get_url(item: str) -> str:
    """construct wikidata api endpoint.

    Returns:
        The wikidata api url.
    """
    url = (
        f"https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=item&continue=0"
        f"&search={'+'.join(item.split())} "
    )
    return url


def generate_file_name(file_name: str) -> str:
    """generate file name of new yaml file to be created.

    Args:
        file_name: name of old yaml file.
    Returns:
        file name of new file.
    """
    suffix = ".yaml" if file_name.endswith(".yaml") else ".yml"
    refined_file_name = file_name.removesuffix(suffix) + "_refined" + suffix
    if file_name.startswith("okh"):
        return refined_file_name
    return "okh_" + refined_file_name


def read_yaml_file(path: Path) -> dict:
    """reads content in yaml file

    Args:
        path: source_path to yaml file.
    Returns:
        file contents
    """
    with open(path, "rb") as file_stream:
        try:
            return yaml.safe_load(file_stream)
        except yaml.YAMLError:
            console.print_exception()


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
                response = requests.get(get_url(sub_item)).json()
                if response["search"]:
                    # get the first result from the search results for now
                    item_dict["identifier"] = response["search"][0]["id"]
                    item_dict["link"] = re.sub(
                        "//www.", "https://", response["search"][0]["url"]
                    )
                    break
                console.print(f"\t[red]couldn't find wikidata for {sub_item}")
            item_list.append(item_dict)
    return item_list
