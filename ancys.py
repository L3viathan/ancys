from random import shuffle
from math import sqrt

import click

from parser import parse
from evaluator import evaluate

class RandomList(list):
    def __init__(self, items):
        super().__init__(items)
        shuffle(self)
        self.ids = {item[2] for item in self}
    def append(self, item, noshuffle=False):
        if item[2] not in self.ids:
            super().append(item)
            self.ids.add(item[2])
            if not noshuffle:
                shuffle(self)
    def extend(self, items):
        for item in items:
            self.append(item, True)
            self.ids.add(item[2])
        shuffle(self)
    def pop(self):
        result = super().pop()
        self.ids.remove(result[2])
        return result

@click.command()
@click.argument("filename")
def ancys(filename):
    evaluated = {}
    environment = {"print": lambda x: print(x) or True, "sqrt": sqrt}
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
