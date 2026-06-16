from dataclasses import dataclass
from typing import Any
from lark import Lark, Transformer
from ast import literal_eval
from . import Node
from importlib import resources



class AmlError(Exception):
    pass

@dataclass
class Text:
    name: str

@dataclass
class Attr:
    k: str
    v: Any

class Trans(Transformer):
    def INT(self, args):
        return int(args)

    def FLOAT(self, args):
        return float(args)
    
    def STR(self, args: str):
        return literal_eval(args.replace('\n', '\\n'))

    def TEXT(self, args):
        return Text(str(args))
    
    def val(self, args):
        ret = args[0]
        if isinstance(ret, Text):
            ret = ret.name
            match ret:
                case 'null':
                    ret = None
                case 'true':
                    ret = True
                case 'false':
                    ret = False
                case string:
                    ret = string
            return ret
        return ret

    def arr(self, args):
        return args
    
    def attr(self, args):
        return Attr(args[0].name, args[1])
    
    def node(self, args):
        dct = {}
        lst = []
        in_kwp = False
        for i in args[1:]:
            if isinstance(i, Attr):
                in_kwp = True
                if i.k in dct:
                    raise AmlError(f"Duplicated field '{i.k}'")
                dct[i.k] = i.v
            else:
                if in_kwp:
                    raise AmlError(f"Positional parameter '{i}' can not be after keyword parameter")
                lst.append(i)
        return Node(args[0].name, dct, lst)

    def start(self, args):
        return args[0]

parser = Lark(resources.files('aml').joinpath('grammer.lark').read_text('utf-8'), parser='lalr', transformer=Trans())

def loads(s: str) -> Node:
    try:
        return parser.parse(s)
    except Exception as e:
        raise AmlError(str(e))

