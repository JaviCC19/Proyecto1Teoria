from thompson import NFA

def epsilon_closure(nfa: NFA, states):
    stack, closure = list(states), set(states)
    while stack:
        s = stack.pop()
        for sym,v in nfa.transitions.get(s, []):
            if sym == 'ε' and v not in closure:
                closure.add(v); stack.append(v)
    return closure


def move(nfa: NFA, states, symbol: str):
    res = set()
    for s in states:
        for sym,v in nfa.transitions.get(s, []):
            if sym == symbol: res.add(v)
    return res


def nfa_accepts(nfa: NFA, w: str) -> bool:
    current = epsilon_closure(nfa, {nfa.start})
    for ch in w:
        current = epsilon_closure(nfa, move(nfa, current, ch))
    return any(q in nfa.accepts for q in current)
