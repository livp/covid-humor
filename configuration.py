"""Configuration singleton."""

import yaml

from typing import Dict


class Configuration:
    _instance = None

    def __init__(self):
        raise RuntimeError('Configuration is a singleton. Call instance() instead.')

    @classmethod
    def instance(cls):
        """Entry point to the configuration class."""
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls._instance.values_dict: Dict = {}
        return cls._instance

    def load_configuration_file(self, file_name: str):
        """Loads the values of a YAML configuration file.

        Args:
            file_name (str): the name of the configuration file without the .yaml extension.
        """
        if not file_name.endswith(".yaml"):
            file_name += ".yaml"
        with open(file_name) as file:
            configuration_values = yaml.safe_load(file)
        self.values_dict.update(configuration_values)

    def reset(self):
        """Resets all values."""
        self.values_dict = {}

    def get(self, item, default=None):
        if item in self.values_dict.keys():
            return self.values_dict[item]
        else:
            return default

    def __getitem__(self, item):
        if item in self.values_dict.keys():
            return self.values_dict[item]
        else:
            RuntimeError("Unknown configuration key.")

    def __setitem__(self, key, value):
        self.values_dict[key] = value

    def __str__(self):
        return str(self.values_dict)

    def __repr__(self):
        return self.values_dict
