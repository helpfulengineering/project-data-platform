from unittest.mock import patch

from tools.okparser.src.parser import Okh

bom_atoms = [
    {"search": []},
    {
        "search": [
            {
                "id": "Q4902580",
                "url": "https://wikidata.org/wiki/Q4902580",
            },
        ]
    },
]

tool_list_atoms = [
    {
        "search": [
            {
                "id": "Q49013",
                "url": "https://wikidata.org/wiki/Q49013",
            },
        ]
    },
    {
        "search": [
            {
                "id": "Q40847",
                "url": "https://wikidata.org/wiki/Q40847",
            },
        ]
    },
]


@patch(
    "tools.okparser.src.parser.get_wiki_data", side_effect=[bom_atoms, tool_list_atoms]
)
def test_parse_file(mocker, tmp_path):
    file = tmp_path / "test_data.yml"

    file.write_text(
        """
title: Surge Pleated Mask from MakerMask (English)
intended-use: "This is an end-use mask to reduce transmission of infectious diseases, in
  particular COVID-19. "
keywords:
  - mask
  - COVID-19
  - fabric mask
  - infection control   
bom: Freshly washed spunbond NWPP bags, Bias tape or other
  latex-free ties
tool-list: Sewing machine, Scissors and pins
        """
    )
    okh = Okh(file, tmp_path)
    okh.generate_okh()
    okh.save()

    assert okh.bom_atoms == bom_atoms
    assert okh.tool_list_atoms == tool_list_atoms
    assert okh.yaml_content == {
        "bom": "Freshly washed spunbond NWPP bags, Bias tape or other latex-free ties",
        "intended-use": "This is an end-use mask to reduce transmission of infectious "
        "diseases, in particular COVID-19. ",
        "keywords": ["mask", "COVID-19", "fabric mask", "infection control"],
        "title": "Surge Pleated Mask from MakerMask (English)",
        "tool-list": "Sewing machine, Scissors and pins",
    }
    assert (tmp_path / "okh_test_data_refined.yml").exists()
