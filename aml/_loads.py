from dataclasses import dataclass
from lark import Lark, Transformer
from ast import literal_eval
from . import Node
from importlib import resources



class AmlError(Exception):
    pass

@dataclass
class Name:
    name: str

class Trans(Transformer):
    def INT(self, args):
        return int(args)

    def FLOAT(self, args):
        return float(args)
    
    def STR(self, args):
        return literal_eval(args)

    def NAME(self, args):
        return Name(str(args))
    
    def val(self, args):
        ret = args[0]
        if isinstance(ret, Name):
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
        return args[0].name, args[1]
    
    def node(self, args):
        dct = {}
        for i in args[1:]:
            if i[0] in dct:
                raise AmlError(f"Duplicated field '{i[0]}'")
            dct[i[0]] = i[1]
        return Node(args[0].name, dct)

    def start(self, args):
        return args[0]

parser = Lark(resources.files('aml').joinpath('grammer.lark').read_text('utf-8'), parser='lalr', transformer=Trans())

def loads(s: str) -> Node:
    try:
        return parser.parse(s)
    except Exception as e:
        raise AmlError(str(e))

