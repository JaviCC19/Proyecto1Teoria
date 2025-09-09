from graphviz import Digraph
from thompson import NFA
from simulaciones import epsilon_closure, move
from collections import defaultdict

class DFA:
    def __init__(self, start, accepts, transitions, alphabet):
        self.start = start
        self.accepts = set(accepts)
        self.transitions = transitions  # dict: state -> dict: symbol -> state
        self.alphabet = alphabet
        self.states = set(transitions.keys())
    
    def states(self):
        return self.states
    
    def accepts_string(self, w: str) -> bool:
        """Simula el DFA con una cadena de entrada"""
        current = self.start
        for symbol in w:
            if symbol not in self.alphabet:
                return False  # Símbolo no está en el alfabeto
            if current not in self.transitions or symbol not in self.transitions[current]:
                return False  # No hay transición definida
            current = self.transitions[current][symbol]
        return current in self.accepts


def draw_dfa(dfa: DFA, filename: str = 'dfa'):
    """Visualiza el DFA usando Graphviz"""
    dot = Digraph()
    dot.attr(rankdir='LR')
    
    # Nodo de inicio
    dot.node('start', label='', shape='point')
    
    # Estados
    for state in dfa.states:
        shape = 'doublecircle' if state in dfa.accepts else 'circle'
        dot.node(str(state), shape=shape, label=f"q{state}")
    
    # Flecha de inicio
    dot.edge('start', str(dfa.start))
    
    # Transiciones
    for state, transitions in dfa.transitions.items():
        for symbol, target in transitions.items():
            dot.edge(str(state), str(target), label=symbol)
    
    dot.render(filename, format='png', cleanup=True)
    print(f"DFA renderizado: {filename}.png")


def minimize_dfa(dfa: DFA) -> DFA:
    """
    Algoritmo de minimización de DFA usando particionamiento
    """
    # Paso 1: Partición inicial - estados de aceptación vs no aceptación
    partition = [dfa.accepts, dfa.states - dfa.accepts]
    
    # Eliminar conjuntos vacíos
    partition = [p for p in partition if p]
    
    changed = True
    while changed:
        changed = False
        new_partition = []
        
        for group in partition:
            # Dividir el grupo basado en transiciones
            subgroups = defaultdict(list)
            
            for state in group:
                # Crear clave basada en las transiciones de este estado
                key = []
                for symbol in sorted(dfa.alphabet):
                    if state in dfa.transitions and symbol in dfa.transitions[state]:
                        target = dfa.transitions[state][symbol]
                        # Encontrar a qué grupo pertenece el estado destino
                        for i, other_group in enumerate(partition):
                            if target in other_group:
                                key.append(i)
                                break
                        else:
                            key.append(-1)  # Estado destino no encontrado
                    else:
                        key.append(-1)  # No hay transición para este símbolo
                
                key = tuple(key)
                subgroups[key].append(state)
            
            # Si el grupo se dividió, agregar los subgrupos
            if len(subgroups) > 1:
                changed = True
                new_partition.extend(subgroups.values())
            else:
                new_partition.append(group)
        
        partition = new_partition
    
    # Paso 2: Crear el DFA minimizado
    # Mapear cada estado original a su grupo representativo
    state_to_group = {}
    for group in partition:
        representative = min(group)  # Usar el estado con menor número como representante
        for state in group:
            state_to_group[state] = representative
    
    # Crear nuevas transiciones
    new_transitions = {}
    new_accepts = set()
    
    for group in partition:
        representative = min(group)
        new_transitions[representative] = {}
        
        # Verificar si este grupo contiene estados de aceptación
        if any(state in dfa.accepts for state in group):
            new_accepts.add(representative)
        
        # Crear transiciones para el representante
        if representative in dfa.transitions:
            for symbol, target in dfa.transitions[representative].items():
                new_target = state_to_group[target]
                new_transitions[representative][symbol] = new_target
    
    # Encontrar el nuevo estado inicial
    new_start = state_to_group[dfa.start]
    
    return DFA(
        start=new_start,
        accepts=new_accepts,
        transitions=new_transitions,
        alphabet=dfa.alphabet
    )


def draw_minimized_dfa(dfa: DFA, filename: str = 'dfa_minimized'):
    """Visualiza el DFA minimizado usando Graphviz"""
    dot = Digraph()
    dot.attr(rankdir='LR')
    
    # Nodo de inicio
    dot.node('start', label='', shape='point')
    
    # Estados
    for state in dfa.states:
        shape = 'doublecircle' if state in dfa.accepts else 'circle'
        dot.node(str(state), shape=shape, label=f"q{state}")
    
    # Flecha de inicio
    dot.edge('start', str(dfa.start))
    
    # Transiciones
    for state, transitions in dfa.transitions.items():
        for symbol, target in transitions.items():
            dot.edge(str(state), str(target), label=symbol)
    
    dot.render(filename, format='png', cleanup=True)
    print(f"DFA minimizado renderizado: {filename}.png")


def compare_automata(nfa: NFA, dfa: DFA, test_strings: list) -> None:
    """Compara el comportamiento del NFA original con el DFA resultante"""
    from simulaciones import nfa_accepts
    
    print("\n--- Comparación de Autómatas ---")
    print(f"NFA estados: {len(nfa.states())}")
    print(f"DFA estados: {len(dfa.states)}")
    print(f"Alfabeto: {sorted(dfa.alphabet)}")
    
    print("\nPruebas de cadenas:")
    for test_str in test_strings:
        nfa_result = nfa_accepts(nfa, test_str)
        dfa_result = dfa.accepts_string(test_str)
        dfa_minimized = minimize_dfa(dfa)
        status = "✓" if nfa_result == dfa_result else "✗"
        print(f"  '{test_str}': NFA={nfa_result}, DFA={dfa_result}, DFA Minimized={dfa_minimized.accepts_string(test_str)} {status}")
