"""Unit tests for okh validator"""
import pytest


@pytest.mark.parametrize("src_fixture", ["okh_yaml_file", "okh_dict"])
def test_okh_validate(okh_validator, src_fixture, request):
    """Test that the OKH validator return the correct boolean
    on validate.

    Args:
        okh_validator: OKHValidator instance.
        src_fixture: src dict or file containing all required OKH fields.
    """
    assert okh_validator.validate(request.getfixturevalue(src_fixture))


def test_okh_validate_partial_fields(okh_validator, okh_dict_partial):
    """Test that the OKH validator return the correct boolean
    on validate.

    Args:
        okh_validator: OKHValidator instance.
        okh_dict_partial: Yaml dict with missing required OKH fields.
    """
    assert not okh_validator.validate(okh_dict_partial)
