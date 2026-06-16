from dataclasses import fields as get_fields, is_dataclass, Field
from typing import Any, Iterable
import typing
from beartype.door import is_bearable
from beartype.roar import BeartypeDecorHintForwardRefException
from inspect import isclass
from . import Node, dumps, loads




class SchemaError(Exception):
    pass

class NodesDecl:
    def __init_subclass__(cls) -> None:
        cls._datacls = {i.__name__: i for i in cls.__dict__.values() if is_dataclass(i) and isclass(i)}


class Schema:
    def __init__(self, nodes: Iterable[type] | type[NodesDecl], check_type = True, annotation_namespace: dict = None) -> None:
        self._check_type = check_type
        self._namespace = typing.__dict__.copy()
        if annotation_namespace:
            self._namespace.update(annotation_namespace)
        if isinstance(nodes, Iterable):
            if any(not (is_dataclass(i) and isclass(i)) for i in nodes):
                raise SchemaError('Datacls must be list of dataclass')
            self._datacls = {i.__name__: i for i in nodes}
            self._namespace.update(self._datacls)
        elif issubclass(nodes, NodesDecl):
            self._datacls = nodes._datacls
            self._namespace.update(nodes.__dict__)
            self._namespace.update({nodes.__name__: nodes})
        else:
            raise SchemaError('Expected Iterable[type] | type[NodesDecl]')
    
    def _create_datacls(self, datacls: type, **kw):
        fields: list[Field] = get_fields(datacls)
        if self._check_type:
            for i in fields:
                if i.name not in kw:
                    continue
                value = kw[i.name]
                if not isinstance(i.type, str):
                    raise SchemaError(f'Annotation {i.type} is not str')
                
                try:
                    if not is_bearable(value, eval(i.type, globals=self._namespace)):
                        raise SchemaError(f"{datacls.__name__}.{i.name} expected {i.type}, got {value}")
                except NameError as e:
                    raise SchemaError(f'When evaluate annotation {i.type} can not fount name {e.name}')
                except BeartypeDecorHintForwardRefException:
                    raise SchemaError(f'Probably caused by the expression {i.type} contains str')
        try:
            return datacls(**kw)
        except TypeError:
            raise SchemaError(f'Probably the fields are wrong. {', '.join(kw)}')
    
    def _node_to_cls(self, obj):
        if isinstance(obj, Node):
            if obj.type not in self._datacls:
                raise SchemaError(f"Dataclass '{obj.type}' not found")
            cls = self._datacls[obj.type]
            return self._create_datacls(cls, **{k: self._node_to_cls(obj[k]) for k in obj})
        if isinstance(obj, list):
            return [self._node_to_cls(i) for i in obj]
        return obj
    
    def _cls_to_node(self, cls):
        if is_dataclass(cls):
            fields = [i.name for i in get_fields(cls)]
            return Node(cls.__class__.__name__, {k: self._cls_to_node(getattr(cls, k)) for k in fields})
        if isinstance(cls, list):
            return [self._cls_to_node(i) for i in cls]
        return cls

    def loads(self, s: str) -> Any:
        obj = loads(s)
        return self._node_to_cls(obj)
    
    def dumps(self, datacls) -> str:
        node = self._cls_to_node(datacls)
        return dumps(node)
