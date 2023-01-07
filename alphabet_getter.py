import os
import ast


class CodeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.code_list = []

    def generic_visit(self, node):
        self.code_list.append(type(node))
        super().generic_visit(node)


def code_to_list(code):
    c = CodeVisitor()
    tree = ast.parse(code)
    c.visit(tree)
    return c.code_list


types = {}
for name in os.listdir('files'):

    with open(f'files/{name}', encoding='utf8') as file:
        for line in code_to_list(file.read()):
            if line in types:
                types[line] += 1
            else:
                types[line] = 1

print(*sorted(types.items(), key=lambda x: x[1], reverse=True), sep='\n')
alphabet = [name for name, value in filter(lambda x: x[1] > 380, types.items())]


