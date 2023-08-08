"""Open knowledge validator"""
import yaml
from pathlib import Path
from typing import List, Union
from collections import namedtuple

Error = namedtuple("Error", ["type", "msg"])


class OKValidator:
    def __init__(self, required_fields: List[str]):
        self.required_fields = required_fields

    def _validate_yaml(self, yaml_content: dict) -> bool:
        """Validate the YAML content to check if it contains the required fields.

        Args:
            yaml_content: The parsed yaml dictionary.
        """
        for field in self.required_fields:
            if field not in yaml_content:
                return False
        return True

    def validate(self, src: Union[str, Path, dict], raise_exception=False) -> bool:
        """
        Validate the YAML source, which can be a file path, YAML content string,
        Path object, or YAML dictionary.

        Args:
            src: The string path or parsed yaml contents represented as dictionary.
            raise_exception: Raises an exception if true otherwise returns a boolean result.
        """
        if not isinstance(src, Union[str, dict, Path]):
            return self.return_value_or_error(
                Error(
                    ValueError,
                    "`src` should be one of the following: a string path, "
                    "a Path object, or Yaml dict",
                ),
                raise_exception,
            )

        if isinstance(src, dict):
            return self._validate_yaml(src)

        if isinstance(src, Path):
            src = str(src)

        try:
            with open(src, "r") as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)
                if yaml_content is None:
                    return self.return_value_or_error(
                        Error(
                            ValueError,
                            "The YAML file is empty or contains invalid syntax.",
                        ),
                        raise_exception,
                    )
                else:
                    return self._validate_yaml(yaml_content)
        except FileNotFoundError:
            return self.return_value_or_error(
                Error(
                    FileNotFoundError,
                    "File not found. Please provide a valid YAML " "file path.",
                ),
                raise_exception,
            )
        except yaml.YAMLError:
            return self.return_value_or_error(
                Error(yaml.YAMLError, "The YAML file is empty or contains invalid syntax."), raise_exception
            )

    @staticmethod
    def return_value_or_error(result: Error, raise_exception: bool = False):
        """Return a bool or raise an exception.

        Args:
            result: Exception to raise.
            raise_exception: If set to true, the provided exception will be raised.
        """
        if not raise_exception:
            return False

        if not isinstance(result, Error):
            raise TypeError(
                f"result arg needs to be of type,{type(Error)}. "
                f"Got {type(result)} instead."
            )

        raise result.type(result.msg)
