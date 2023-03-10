import argparse
import ast


alphabet = [ast.Import,
            ast.alias,
            ast.ImportFrom,
            ast.ClassDef,
            ast.Name,
            ast.Load,
            ast.Expr,
            ast.Constant,
            ast.FunctionDef,
            ast.arguments,
            ast.arg,
            ast.Subscript,
            ast.Index,
            ast.Assign,
            ast.Attribute,
            ast.Store,
            ast.If,
            ast.Call,
            ast.Return,
            ast.ExtSlice,
            ast.Slice,
            ast.BinOp,
            ast.Add,
            ast.keyword,
            ast.List,
            ast.Tuple,
            ast.Sub,
            ast.Compare,
            ast.Eq,
            ast.For,
            ast.Mult,
            ast.Div,
            ast.Raise,
            ast.UnaryOp,
            ast.USub,
            ast.Dict,
            ast.comprehension,
            ast.Assert]
alphabet_mapping = {word: index for index, word in enumerate(alphabet)}


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

parser = argparse.ArgumentParser(description='???????????????? ???? ??????????????????????')
parser.add_argument('input', type=str, help='?????????????????? ?????? ??????????????????')
parser.add_argument('output', type=str, help='???????? ?????? ???????????? ????????????????????')
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
