from dataclasses import fields as get_fields, is_dataclass, Field
from typing import Any, Callable
import typing
from beartype.door import is_bearable
from beartype.roar import BeartypeDecorHintForwardRefException
from inspect import isclass
from . import Node, dumps, loads




class SchemaError(Exception):
    pass



class Schema[Start]:
    def __init__(self, nodes: type, *, check_type = True, start: type[Start] = None, hook: Callable[[Any], Any] = None) -> None:
        self._check_type = check_type
        self._start = start
        self._hook = hook
        self._namespace = typing.__dict__.copy()
        if isclass(nodes):
            self._datacls = {i.__name__: i for i in nodes.__dict__.values() if is_dataclass(i) and isclass(i)}
            self._namespace.update(nodes.__dict__)
            self._namespace.update({nodes.__name__: nodes})
        else:
            raise SchemaError(f'Expected class, got {nodes}')
        
    def _check(self, val, type, f_name, cls):
        try:
            if not is_bearable(val, eval(type, globals=self._namespace)):
                raise SchemaError(f"{cls.__name__}.{f_name} expected {type}, got {val}")
        except NameError as e:
            raise SchemaError(f'When evaluate annotation {type} can not fount name {e.name}')
        except BeartypeDecorHintForwardRefException:
            raise SchemaError(f'Probably caused by the expression {type} contains str')
    
    def _create_datacls(self, datacls: type, *a, **kw):
        fields: list[Field] = get_fields(datacls)
        if self._check_type:
            for i in fields:
                if i.name not in kw:
                    continue
                value = kw[i.name]
                if not isinstance(i.type, str):
                    raise SchemaError(f'Annotation {i.type} is not str')
                self._check(value, i.type, i.name, datacls)
            if len(a) > len(fields):
                raise SchemaError('Positional parameters are too many')
            for v, f in zip(a, fields):
                self._check(v, f.type, f.name, datacls)
        try:
            return datacls(*a, **kw)
        except TypeError:
            raise SchemaError(f'Probably the parameters are wrong. {', '.join(a)}{', ' if kw else ''}{', '.join(kw)}')
    
    def _node_to_cls(self, obj):
        if isinstance(obj, Node):
            if obj.type not in self._datacls:
                raise SchemaError(f"Dataclass '{obj.type}' not found")
            cls = self._datacls[obj.type]
            ret = self._create_datacls(cls, *[self._node_to_cls(i) for i in obj.list], **{k: self._node_to_cls(obj[k]) for k in obj})
        elif isinstance(obj, list):
            ret = [self._node_to_cls(i) for i in obj]
        else:
            ret = obj
        if self._hook:
            new = self._hook(ret)
            if new is not None:
                return new
        return ret
    
    def _cls_to_node(self, cls):
        if is_dataclass(cls):
            fields = [i.name for i in get_fields(cls)]
            return Node(cls.__class__.__name__, {k: self._cls_to_node(getattr(cls, k)) for k in fields}, [])
        if isinstance(cls, list):
            return [self._cls_to_node(i) for i in cls]
        return cls

    def loads(self, s: str) -> Start:
        obj = loads(s)
        ret =  self._node_to_cls(obj)
        if (self._start is not None) and (not is_bearable(ret, self._start)):
            raise SchemaError(f"Start expected {self._start}, got {ret}")
        return ret
    
    def dumps(self, datacls) -> str:
        node = self._cls_to_node(datacls)
        return dumps(node)
