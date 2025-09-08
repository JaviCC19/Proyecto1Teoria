import os
from shunting_yard import build_ast_from_infix, draw_ast
from thompson import thompson_from_ast, draw_nfa
from simulaciones import nfa_accepts
from dfa_construction import minimize_dfa, draw_dfa, draw_minimized_dfa, compare_automata
from subset import subset_construction, get_alphabet

def process_files(path_regex: str, path_words: str|None=None, single_w: str|None=None, render_ast: bool=False, build_dfa: bool=True, minimize_dfa_flag: bool=True):
    if not os.path.exists(path_regex):
        print(f"Error: no existe el archivo {path_regex}")
        return
    with open(path_regex, 'r', encoding='utf-8') as f:
        regexes = [line.strip() for line in f if line.strip()]
    palabras = None
    if single_w is not None:
        palabras = [single_w]*len(regexes)
    elif path_words is not None and os.path.exists(path_words):
        with open(path_words, 'r', encoding='utf-8') as fw:
            palabras = [line.strip() for line in fw]
        m = min(len(regexes), len(palabras))
        regexes, palabras = regexes[:m], palabras[:m]
    
    for i,r in enumerate(regexes,1):
        print(f"\n--- Expresión {i} ---")
        expanded, postfix, ast = build_ast_from_infix(r)
        print(f"Expandida: {expanded}")
        print(f"Postfix  : {postfix}")
        if render_ast: draw_ast(ast, f'ast_expr_{i}')
        
        # Construir NFA
        nfa = thompson_from_ast(ast)
        draw_nfa(nfa, f'nfa_expr_{i}')
        
        # Construir DFA usando construcción de subconjuntos
        if build_dfa:
            print(f"\n--- Construcción de DFA (Subconjuntos) ---")
            dfa = subset_construction(nfa)
            draw_dfa(dfa, f'dfa_expr_{i}')
            print(f"DFA construido con {len(dfa.states)} estados")
            
            # Minimizar DFA
            if minimize_dfa_flag:
                print(f"\n--- Minimización de DFA ---")
                minimized_dfa = minimize_dfa(dfa)
                draw_minimized_dfa(minimized_dfa, f'dfa_minimized_expr_{i}')
                print(f"DFA minimizado con {len(minimized_dfa.states)} estados")
                
                # Comparar autómatas
                test_strings = palabras[i-1:i] if palabras else ['a', 'b', 'ab', 'ba', 'aa', 'bb', 'aba', 'bab']
                compare_automata(nfa, minimized_dfa, test_strings)
        
        if palabras:
            w = palabras[i-1]
            ok = nfa_accepts(nfa, w)
            print(f"w='{w}' -> {'sí' if ok else 'no'}")



ruta_expresiones = "expresiones.txt"
cadena_unica = "bbb"
process_files(ruta_expresiones, single_w=cadena_unica, render_ast=True)
