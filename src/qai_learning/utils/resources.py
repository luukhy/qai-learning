import json
from importlib import resources

_RESOUCE_MAP = {
    "graph_config": "graph_config.json",
    "graph_state": "graph_state.json",
    "user_answers": "user_answers.json",
}


def load_json(name: str):
    filename = _RESOUCE_MAP[name]
    path = resources.files("qai_learning.data").joinpath(filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Couldn't open {path}: {e}")
        return {}


def save_json(name: str, contents: dict):
    filename = _RESOUCE_MAP[name]
    path = resources.files("qai_learning.data").joinpath(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(contents, f, indent=4)
    return {}
