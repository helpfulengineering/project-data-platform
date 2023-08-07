"""Unit tests for ok validator"""

import pytest
from tools.ok_validator.src.validate import OKValidator, Error


@pytest.fixture
def okh_string():
    return """
title: mock okh title.
description: mock description for okh.
bom: mock bom field.
        """


@pytest.fixture
def okh_yaml_file(tmp_path, okh_string):
    (okh_file := tmp_path / "okh.yaml").touch()
    okh_file.write_text(okh_string)

    return okh_file


@pytest.fixture
def okh_dict():
    return {"title": "mock okh title.", "description": "mock description for okh.", "bom": "mock bom field."}


@pytest.fixture
def ok_validator():
    return OKValidator(["bom", "title"])


@pytest.mark.parametrize(
    "fixture", ["okh_yaml_file", "okh_dict"]
)
def test_validate_yaml_file(fixture, request, ok_validator):
    """Test that the validate method returns the correct boolean.

    Args:
        fixture: fixtures of accepted src formats.
        request: pytest request.
        ok_validator: Validator instance.
    """
    okh = request.getfixturevalue(fixture)
    assert ok_validator.validate(okh)


def test_validate_with_non_existent_file(tmp_path, ok_validator):
    """Test that the validate method returns False when file does not
        exist.

        Args:
            tmp_path: Test location.
            ok_validator: Validator instance.
    """
    file = tmp_path / "okh.yaml"
    assert not ok_validator.validate(file)


def test_validate_with_invalid_file(tmp_path, ok_validator):
    """Test that the validate method returns False when an invalid Yaml file
        is passed.

        Args:
            tmp_path: Test location.
            ok_validator: Validator Instance.
    """
    (file := tmp_path / "okh.yaml").touch()
    assert not ok_validator.validate(file)

    file.write_text("""title: invalid_field: mock title
description: mock description.
    """)

    assert not ok_validator.validate(file)


def test_validate_raise_exception(tmp_path, ok_validator):
    """Test that an exception is raised when the raise_exception parameter
        is set to True on the validator method.

        Args:
            tmp_path: The test location.
            ok_validator: Validator instance.
    """
    file = tmp_path / "okh.yaml"

    with pytest.raises(FileNotFoundError):
        ok_validator.validate(file, raise_exception=True)


def test_return_value_or_error():
    """Test that the right exception is raised."""

    error = Error(type=ValueError, msg="raised a value error")
    with pytest.raises(error.type) as err:
        OKValidator.return_value_or_error(error, raise_exception=True)
    assert err.value.args[0] == error.msg


def test_return_value_or_error_with_wrong_error_type():
    """Test that an exception is raised when the wrong type is provided
        with the `raise_exception` flag set to True.
    """
    with pytest.raises(TypeError):
        OKValidator.return_value_or_error(str, raise_exception=True)
