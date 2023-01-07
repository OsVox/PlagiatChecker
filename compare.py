import argparse
import ast
from constants import *


def read_code(name):
    with open(name, encoding='utf8') as f:
        file = f.read()
    return file


class CodeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.code_list = []

    def generic_visit(self, node):
        self.code_list.append(type(node))
        super().generic_visit(node)


class Model:

    @staticmethod
    def preprocessing(code):
        c = CodeVisitor()
        tree = ast.parse(code)
        c.visit(tree)
        return list(map(lambda x: alphabet_mapping[x], filter(lambda x: x in alphabet, c.code_list)))

    @staticmethod
    def wagner_fisher(code1: list, code2: list, shift=0.05, rep_cost=1):
        prev_line = [j for j in range(len(code2))]
        new_line = [0] * len(code2)
        for i in range(len(code1)):
            for j in range(len(code2)):
                if j == 0:
                    new_line[0] = i * 1
                else:
                    new_line[j] = min(prev_line[j] + 1,
                                      new_line[j - 1] + 1,
                                      prev_line[j - 1] + rep_cost * (code1[i] != code2[j]))
            prev_line, new_line = new_line, [0] * len(code2)
        try:
            return min(1.0, shift + 1 - prev_line[-1] / (rep_cost * max(len(code2), len(code1))))
        except IndexError:
            if len(code1) == len(code2):
                return 1
            return 0

    def __init__(self, rep_cost=1, shift=0.05):
        self.rep_cost = rep_cost
        self.shift = shift

    def predict(self, code1, code2):
        try:
            return Model.wagner_fisher(code1, code2, self.shift, self.rep_cost)
        except SyntaxError:
            return 0


anti_plag = Model()

parser = argparse.ArgumentParser(description='Проверка на антиплагиат')
parser.add_argument('input', type=str, help='Программы для сравнения')
parser.add_argument('output', type=str, help='Файл для записи результата')
args = parser.parse_args()

scores = []
with open(args.input, 'r', encoding='utf8') as inp:
    for line in inp:
        try:
            orig, candidate = map(lambda x: Model.preprocessing(read_code(x)), line.split())
            scores.append(anti_plag.predict(orig, candidate))
        except SyntaxError:
            scores.append(0)

with open(args.output, 'w') as output:
    for score in scores:
        output.write(str(score) + '\n')
