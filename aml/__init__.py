class Node(dict):
    def __init__(self, type: str, dct: dict):
        super().__init__(dct)
        self.type = type
    def __repr__(self) -> str:
        return self.type + super().__repr__()

from ._loads import loads, AmlError
from ._dumps import dumps
from ._schema import Schema, SchemaError, NodesDecl
