"""Open knowledge validator"""
import json
from pathlib import Path
from typing import Type, TypeVar, Union
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_file_as, parse_yaml_raw_as

T = TypeVar("T", bound=BaseModel)


class OKValidator:
    def __init__(self, model_type: Type[T]):
        self.model_type = model_type

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
                ValueError(
                    "`src` should be one of the following: a string path, "
                    "a Path object, or Yaml dict",
                ),
                raise_exception,
            )
        try:
            if isinstance(src, dict):
                parse_yaml_raw_as(self.model_type, json.dumps(src))
            else:
                parse_yaml_file_as(self.model_type, src)
            return True
        except Exception as err:
            return self.return_value_or_error(err, raise_exception)

    @staticmethod
    def return_value_or_error(error: Exception, raise_exception: bool = False):
        """Return a bool or raise an exception.

        Args:
            error: Exception to raise.
            raise_exception: If set to true, the provided exception will be raised.
        """
        if not raise_exception:
            return False
        raise error
