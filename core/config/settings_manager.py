from pathlib import Path
import yaml


CONFIG_PATH = Path("cosmo/core/config/settings.yaml")


class Config:

    def __init__(self):

        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

    def get(self, *keys, default=None):

        value = self.data

        for key in keys:

            if key not in value:
                return default

            value = value[key]

        return value


config = Config()