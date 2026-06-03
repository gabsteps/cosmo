from pathlib import Path
import yaml


CONFIG_PATH = (
    Path(__file__)
    .resolve()
    .parent
    / "settings.yaml"
)


class Config:

    def __init__(self):

        with open(
            CONFIG_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            self.data = yaml.safe_load(file)

    def get(
        self,
        *keys,
        default=None
    ):

        value = self.data

        for key in keys:

            if not isinstance(value, dict):
                return default

            if key not in value:
                return default

            value = value[key]

        return value


config = Config()