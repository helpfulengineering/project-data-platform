import pytest

from tools.okparser.src.utils import get_url, generate_file_name


def test_get_url():
    assert (
        get_url("sewing machine")
        == "https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json"
        "&language=en&type=item&continue=0&search=sewing+machine "
    )


@pytest.mark.parametrize(
    "file_name,expected",
    [
        ("test_data.yml", "okh_test_data_refined.yml"),
        ("test_data.yaml", "okh_test_data_refined.yaml"),
        ("okh_test_data.yml", "okh_test_data_refined.yml"),
        ("okh_test_data.yaml", "okh_test_data_refined.yaml"),
    ],
)
def test_generate_file_name(file_name, expected):
    assert generate_file_name(file_name) == expected
