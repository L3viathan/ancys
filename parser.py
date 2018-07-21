import json
import itertools

import tatsu
from tatsu.util import asjson

grammar = r"""
@@grammar::ANCYS

@@keyword::if else for in true false

start = { expression ';' } $;

expression = assignment | call | op | literal | datastructure |
controlstructure | name ;

assignment = assignment:(name '=' expression) ;

call = call:(name '(' expression ')') ;  # might put expre list here later

op = op:((expression binop expression) | (unop expression)) ;

literal = int | float | string | bool ;

datastructure = list ;

controlstructure = if | for | while ;

binop = '+' | '*' | '-' | '/' | '==' | '!=' | 'and' | 'or' ;
unop = '+' | '-' | '!' ;

@name
name = name:(/[A-Za-z0-9_]+/);

int = int:('0' | /[1-9][0-9]*/) ;
float = float:(/[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)/) ;
string = '"' string:(/([^"\\]|\\[\\"nt])*/) '"' ;
bool = bool:('true' | 'false') ;

list = list:('[' ','%{ expression } ']') ;

if = if:('if' expression '{' expressions '}') ;
for = for:('for' name 'in' expression '{' expressions '}') ;
while = while:('while' expression '{' expressions '}') ;

expressions = { expression ';' }+ ;
"""

def parse_expression(expr, counter):
    type_, values = expr.popitem()

    if type_ == "assignment":
        return (
            "assignment",
            {
                "name": values[0]["name"],
                "value": parse_expression(values[2], counter),
            },
            next(counter),
        )
    elif type_ == "op":
        if len(values) == 3:
            return (
                "binop",
                {
                    "operation": values[1],
                    "left": parse_expression(values[0], counter),
                    "right": parse_expression(values[2], counter),
                },
                next(counter),
            )
        else:
            assert len(values) == 2
            return (
                "unop",
                {
                    "operation": values[0],
                    "right": parse_expression(values[1], counter),
                },
                next(counter),
            )
    elif type_ == "int":
        return ("int", int(values), next(counter))
    elif type_ == "float":
        return ("float", float(values), next(counter))
    elif type_ == "string":
        return ("string", str(values), next(counter))
    elif type_ == "bool":
        return ("bool", values == "true", next(counter))
    elif type_ == "call":
        return (
            "call",
            {
                "function": parse_expression(values[0], counter),
                "argument": parse_expression(values[2], counter),
            },
            next(counter),
        )
    elif type_ == "for":
        return (
            "for",
            {
                "name": values[1]["name"],
                "argument": parse_expression(values[3], counter),
                "body": parse_statements(values[5], counter),
            },
            next(counter),
        )
    elif type_ == "while":
        return (
            "while",
            {
                "condition": parse_expression(values[1], counter),
                "body": parse_statements(values[3], counter),
            },
            next(counter),
        )
    elif type_ == "list":
        return (
            "list",
            [parse_expression(val, counter) for val in values[1][::2]],
            next(counter),
        )
    elif type_ == "if":
        return (
            "if",
            {
                "condition": parse_expression(values[1], counter),
                "body": parse_statements(values[3], counter),
            },
            next(counter),
        )
    elif type_ == "name":
        return (
            "name",
            values,
            next(counter),
        )
    else:
        print(type_)
        raise NotImplementedError


def parse_statements(ir, counter):
    return [parse_expression(expr, counter) for expr, _ in ir]  # throw away semicolon

def parse(source):
    counter = itertools.count()
    ir = asjson(
        tatsu.parse(
            grammar,
            source,
            eol_comments_re="#.*?$",
        ),
    )

    return parse_statements(ir, counter)



if __name__ == '__main__':
    with open("draft.anc") as f:
        code = f.read()

    ast = parse(code)

    print(json.dumps(ast, indent=4))
