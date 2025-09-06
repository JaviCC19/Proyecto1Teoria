from graphviz import Digraph
from shunting_yard import Node

class NFA:
    def __init__(self, start, accepts, transitions):
        self.start = start
        self.accepts = set(accepts)
        self.transitions = transitions

    def states(self):
        return set(self.transitions.keys()) | set().union(*[set(v for _, v in lst) for lst in self.transitions.values()]) | self.accepts | {self.start}


def new_state(counter):
    s = counter[0]
    counter[0] += 1
    return s


def add_transition(trans, u, sym, v):
    trans.setdefault(u, []).append((sym, v))


def thompson_from_ast(node, counter=None) -> NFA:
    if counter is None:
        counter = [0]

    if node is None:
        s = new_state(counter)
        f = new_state(counter)
        trans = {}
        add_transition(trans, s, 'ε', f)
        return NFA(s, {f}, trans)

    if node.left is None and node.right is None:
        s = new_state(counter)
        f = new_state(counter)
        trans = {}
        add_transition(trans, s, node.value, f)
        return NFA(s, {f}, trans)

    if node.value == '.':
        nfa1 = thompson_from_ast(node.left, counter)
        nfa2 = thompson_from_ast(node.right, counter)
        trans = {}
        for t in (nfa1.transitions, nfa2.transitions):
            for u, lst in t.items():
                for sym, v in lst:
                    add_transition(trans, u, sym, v)
        for a in nfa1.accepts:
            add_transition(trans, a, 'ε', nfa2.start)
        return NFA(nfa1.start, nfa2.accepts, trans)

    if node.value == '|':
        nfaL = thompson_from_ast(node.left, counter)
        nfaR = thompson_from_ast(node.right, counter)
        trans = {}
        for t in (nfaL.transitions, nfaR.transitions):
            for u, lst in t.items():
                for sym, v in lst:
                    add_transition(trans, u, sym, v)
        s = new_state(counter)
        f = new_state(counter)
        add_transition(trans, s, 'ε', nfaL.start)
        add_transition(trans, s, 'ε', nfaR.start)
        for a in nfaL.accepts:
            add_transition(trans, a, 'ε', f)
        for a in nfaR.accepts:
            add_transition(trans, a, 'ε', f)
        return NFA(s, {f}, trans)

    if node.value == '*':
        nfaA = thompson_from_ast(node.left, counter)
        trans = {u: lst[:] for u, lst in nfaA.transitions.items()}
        s = new_state(counter)
        f = new_state(counter)
        add_transition(trans, s, 'ε', nfaA.start)
        add_transition(trans, s, 'ε', f)
        for a in nfaA.accepts:
            add_transition(trans, a, 'ε', nfaA.start)
            add_transition(trans, a, 'ε', f)
        return NFA(s, {f}, trans)

    raise ValueError(f"Operador no soportado en Thompson: {node.value}")


def draw_nfa(nfa: NFA, filename: str = 'nfa'):
    dot = Digraph()
    dot.attr(rankdir='LR')

    dot.node('start', label='', shape='point')

    for q in sorted(nfa.states()):
        shape = 'doublecircle' if q in nfa.accepts else 'circle'
        dot.node(str(q), shape=shape, label=f"q{q}")

    dot.edge('start', str(nfa.start))

    for u, lst in nfa.transitions.items():
        for sym, v in lst:
            dot.edge(str(u), str(v), label=sym)

    dot.render(filename, format='png', cleanup=True)
    print(f"AFN renderizado: {filename}.png")
