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


def read_yaml_file(path) -> dict:
    """reads content in yaml file

    Args:
        path: path to yaml file.
    Returns:
        file contents
    """
    with open(path, "rb") as file_stream:
        try:
            return yaml.safe_load(file_stream)
        except yaml.YAMLError:
            console.print_exception()
