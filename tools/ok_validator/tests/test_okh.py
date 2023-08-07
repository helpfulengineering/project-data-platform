"""Unit tests for okh validator"""


def test_okh_validate(okh_validator, okh_dict):
    """Test that the OKH validator return the correct boolean
    on validate.

    Args:
        okh_validator: OKHValidator instance.
        okh_dict: Yaml dict containing all required OKH fields.
    """
    assert okh_validator.required_fields == ["bom", "title"]
    assert okh_validator.validate(okh_dict)


def test_okh_validate_partial_fields(okh_validator, okh_dict_partial):
    """Test that the OKH validator return the correct boolean
    on validate.

    Args:
        okh_validator: OKHValidator instance.
        okh_dict_partial: Yaml dict with missing required OKH fields.
    """
    assert not okh_validator.validate(okh_dict_partial)
