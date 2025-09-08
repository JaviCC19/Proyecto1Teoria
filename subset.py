from simulaciones import epsilon_closure, move
from dfa_construction import DFA

def get_alphabet(nfa) -> set:
    """Extrae el alfabeto del NFA (excluyendo epsilon)"""
    alphabet = set()
    for transitions in nfa.transitions.values():
        for symbol, _ in transitions:
            if symbol != 'ε':
                alphabet.add(symbol)
    return alphabet


def subset_construction(nfa) -> DFA:
    """
    Algoritmo de construcción de subconjuntos para convertir NFA a DFA
    """
    alphabet = get_alphabet(nfa)
    
    # Estado inicial del DFA es el cierre epsilon del estado inicial del NFA
    initial_state = frozenset(epsilon_closure(nfa, {nfa.start}))
    
    dfa_states = {initial_state}
    dfa_transitions = {}
    dfa_accepts = set()
    unprocessed = [initial_state]
    
    while unprocessed:
        current_dfa_state = unprocessed.pop(0)
        dfa_transitions[current_dfa_state] = {}
        
        if any(nfa_state in nfa.accepts for nfa_state in current_dfa_state):
            dfa_accepts.add(current_dfa_state)
        
        for symbol in alphabet:
            next_nfa_states = move(nfa, current_dfa_state, symbol)
            next_dfa_state = frozenset(epsilon_closure(nfa, next_nfa_states))
            
            if next_dfa_state:
                dfa_transitions[current_dfa_state][symbol] = next_dfa_state
                if next_dfa_state not in dfa_states:
                    dfa_states.add(next_dfa_state)
                    unprocessed.append(next_dfa_state)
    
    # Mapear estados a enteros
    state_map = {state: i for i, state in enumerate(dfa_states)}
    numeric_transitions = {}
    
    for dfa_state, transitions in dfa_transitions.items():
        numeric_state = state_map[dfa_state]
        numeric_transitions[numeric_state] = {}
        for symbol, target_state in transitions.items():
            numeric_transitions[numeric_state][symbol] = state_map[target_state]
    
    numeric_accepts = {state_map[state] for state in dfa_accepts}
    
    return DFA(
        start=state_map[initial_state],
        accepts=numeric_accepts,
        transitions=numeric_transitions,
        alphabet=alphabet
    )
