class Node(dict):
    def __init__(self, type: str, dct: dict, lst: list):
        super().__init__(dct)
        self.type = type
        self.list = lst
    def __repr__(self) -> str:
        return self.type + "{" + ' '.join(repr(i) for i in self.list) + (' ' if self else '') + ' '.join(f'{k}: {repr(v)}' for k, v in self.items()) + "}"

from ._loads import loads, AmlError
from ._dumps import dumps
from ._schema import Schema, SchemaError
