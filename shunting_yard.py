from graphviz import Digraph

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def expand_regex(regex: str) -> str:
    result = ''
    i = 0
    while i < len(regex):
        c = regex[i]

        if i + 1 < len(regex) and regex[i + 1] in {'+', '?'}:
            op = regex[i + 1]
            if c == ')':
                j = i
                count = 0
                while j >= 0:
                    if regex[j] == ')':
                        count += 1
                    elif regex[j] == '(':
                        count -= 1
                        if count == 0:
                            break
                    j -= 1
                group = regex[j:i+1]
                if op == '+':
                    result += f"{group}.{group}*"
                else:
                    result += f"{group}|ε"
            else:
                if op == '+':
                    result += f"{c}.{c}*"
                else:
                    result += f"{c}|ε"
            i += 2
        else:
            result += c
            i += 1
    return result


def get_precedence(c: str) -> int:
    precedencia = {
        '(': 1,
        '|': 2,
        '.': 3,
        '?': 4,
        '*': 4,
        '+': 4,
        '^': 5
    }
    return precedencia.get(c, 6)


def format_regex(regex: str) -> str:
    res = ""
    all_ops = {'|', '?', '+', '*', '.', '^'}
    binarios = {'*', '+', '?'}

    def is_operand(c: str) -> bool:
        return c not in all_ops and c not in {'(', ')', '[', ']', '{', '}'}

    i = 0
    while i < len(regex) - 1:
        c1 = regex[i]
        c2 = regex[i + 1]
        res += c1

        if (
            (is_operand(c1) or c1 in binarios or c1 in {')', ']'}) and
            (is_operand(c2) or c2 in {'(', '['})
        ):
            res += '.'
        i += 1

    if i < len(regex):
        res += regex[-1]
    return res


def infix_to_postfix(regex: str) -> str:
    output = ''
    stack = []
    formatted = format_regex(regex)
    print(f"\nInfix original : {regex}")
    print(f"Infix formateado: {formatted}")
    print("Pasos de conversión:")

    for c in formatted:
        if c == '(':
            stack.append(c)
            print(f"Push '(': {stack}")
        elif c == ')':
            while stack and stack[-1] != '(':
                output += stack.pop()
                print(f"Pop hasta '(': salida = {output}, stack = {stack}")
            stack.pop()
            print(f"Eliminar '(': {stack}")
        elif c in "|.+?^*":
            while stack and get_precedence(stack[-1]) >= get_precedence(c):
                output += stack.pop()
                print(f"Pop por precedencia: salida = {output}, stack = {stack}")
            stack.append(c)
            print(f"Push operador '{c}': {stack}")
        else:
            output += c
            print(f"Añadir operando '{c}' a salida: {output}")

    while stack:
        output += stack.pop()
        print(f"Vaciar stack: salida = {output}")

    print(f"Postfix final  : {output}")
    return output


def postfix_to_ast(postfix: str):
    stack = []
    for token in postfix:
        if token in {'.', '|'}:
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(token, left, right))
        elif token in {'*'}:
            node = stack.pop()
            stack.append(Node(token, node))
        else:
            stack.append(Node(token))
    return stack[0] if stack else None


def draw_ast(root, filename='ast'):
    dot = Digraph()

    def add_nodes_edges(node, counter=[0]):
        node_id = str(counter[0])
        dot.node(node_id, node.value)
        current_id = node_id
        counter[0] += 1
        if node.left:
            left_id = add_nodes_edges(node.left, counter)
            dot.edge(current_id, left_id)
        if node.right:
            right_id = add_nodes_edges(node.right, counter)
            dot.edge(current_id, right_id)
        return current_id

    if root:
        add_nodes_edges(root)
        dot.render(filename, format='png', cleanup=True)
        print(f"Árbol generado: {filename}.png")


def build_ast_from_infix(regex: str):
    expanded = expand_regex(regex)
    postfix = infix_to_postfix(expanded)
    ast = postfix_to_ast(postfix)
    return expanded, postfix, ast
