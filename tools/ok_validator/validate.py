"""Open knowledge validator"""
import yaml
from pathlib import Path
from typing import List, Union


class OKValidator:
    def __init__(self, required_fields: List[str]):
        self.required_fields = required_fields

    def _validate_yaml(self, yaml_content: dict) -> bool:
        """
        Validate the YAML content to check if it contains the required fields.
        """
        for field in self.required_fields:
            if field not in yaml_content:
                return False
        return True

    def validate(self, src: Union[str, Path, dict]) -> bool:
        """
        Validate the YAML source, which can be a file path, YAML content string, Path object, or YAML dictionary.
        """
        if not isinstance(src, Union[str, dict]):
            raise TypeError("src should be one of the following: a string path, a yaml string content,  "
                            "a Path object, or Yaml dict")

        if isinstance(src, dict):
            return self._validate_yaml(src)

        if isinstance(src, Path):
            src = str(src)

        try:
            with open(src, 'r') as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)
                if yaml_content is None:
                    print("Error: The YAML file is empty or contains invalid syntax.")
                    return False
                else:
                    return self._validate_yaml(yaml_content)
        except FileNotFoundError:
            print("Error: File not found. Please provide a valid YAML file path.")
            return False
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML syntax. {e}")
            return False
