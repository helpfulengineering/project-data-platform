import pytest

from tools.ok_validator.src.validate import OKValidator
from tools.ok_validator.src.okh import OKHValidator


@pytest.fixture
def okh_string():
    return """
title: mock okh title.
description: mock description for okh.
bom: mock bom field.
        """


@pytest.fixture
def okh_yaml_file(tmp_path, okh_string):
    okh_file = tmp_path / "okh.yaml"
    okh_file.touch()
    okh_file.write_text(okh_string)

    return okh_file


@pytest.fixture
def okh_dict():
    return {
        "title": "mock okh title.",
        "description": "mock description for okh.",
        "bom": "mock bom field.",
    }


@pytest.fixture
def okh_dict_partial():
    return {"title": "mock okh title."}


@pytest.fixture
def ok_validator():
    return OKValidator(["bom", "title"])


@pytest.fixture
def okh_validator():
    return OKHValidator()
