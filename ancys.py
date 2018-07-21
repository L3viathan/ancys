from random import shuffle

import click

from parser import parse
from evaluator import evaluate

class RandomList(list):
    def __init__(self, items):
        super().__init__(items)
        shuffle(self)
    def append(self, item):
        super().append(item)
        shuffle(self)
    def extend(self, items):
        super().extend(items)
        shuffle(self)

@click.command()
@click.argument("filename")
def ancys(filename):
    evaluated = {}
    environment = {"print": print}
    with open(filename) as f:
        source = f.read()
        expressions = RandomList(parse(source))  # for now a weird list hack
    while expressions:
        expr = expressions.pop()
        if evaluate(*expr, expressions, evaluated, environment):  # evaluation successful
            pass
        else:
            expressions.append(expr)



if __name__ == '__main__':
    ancys()
