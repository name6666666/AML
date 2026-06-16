from . import Node



INDENT = 4

def node(type: str, dct: Node, indent: int):
    indent_str = (indent + INDENT) * ' '
    ret = f'''{type} {{
{indent_str}{f'\n{indent_str}'.join(f'{trans(i, indent=indent + INDENT)}' for i in dct.list)}
{indent_str}{f'\n{indent_str}'.join(f'{i}: {trans(dct[i], indent=indent + INDENT)}' for i in dct)}
{indent * ' '}}}'''
    return ret

def arr(lst: list, indent: int):
    indent_str = (indent + INDENT) * ' '
    ret = f'''[
{indent_str}{f'\n{indent_str}'.join(trans(i, indent=indent + INDENT) for i in lst)}
{indent * ' '}]'''
    return ret

def trans(obj, indent = 0):
    if isinstance(obj, Node):
        return node(obj.type, obj, indent=indent)
    if isinstance(obj, list):
        return arr(obj, indent=indent)
    if isinstance(obj, bool):
        return 'true' if obj else 'false'
    if obj is None:
        return 'null'
    return repr(obj)

def dumps(obj) -> str:
    return trans(obj)
