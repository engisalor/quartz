import pathlib

import yaml


def load_yaml(file: str):
    filepath = pathlib.Path(file)
    if filepath.exists():
        with open(filepath, "r") as stream:
            dt = yaml.safe_load(stream)
    else:
        raise FileNotFoundError()
    return dt
