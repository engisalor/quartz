import pathlib

import yaml


def load_yaml(file: str):
    with open(file) as stream:
        dt = yaml.safe_load(stream)
    return dt


def load_markdown(file: str, clean_header=True):
    with open(file) as f:
        lines = f.readlines()
    if clean_header:
        lines = [x.lstrip("#") for x in lines]
    return "".join(lines)


def compile_markdown(dir: str, clean_header=False):
    files = pathlib.Path(dir).glob("*.md")
    files = sorted(files)
    texts = [load_markdown(f, clean_header) for f in files]
    return "\n\n".join(texts)
