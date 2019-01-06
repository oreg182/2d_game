import json


class _Config:
    def __init__(self):
        self.confi = None

        self.read_confi()

    def read_confi(self):
        with open("config.json") as f:
            self.confi = json.load(f)[0]


config = _Config()


def get_confi(setting):
    return config.confi[setting]
