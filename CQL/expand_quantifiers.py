#%%
from lexer import Lexer
from tokens import Token, TokenType
from itertools import product
from copy import deepcopy


def expand_quantifiers(tokens: list, max_quant: int=15):
    records = set()

    quantify_info = []
    for i, tk in enumerate(tokens):
        if tk.type.name == 'TOKEN_QUANTIFIER':
            min_ = tk.value[0]
            max_ = tk.value[1] + 1 if tk.value[1] != 'inf' else max_quant
            quantify_info.append([i, 
                list(range(min_, max_))]
            )

    results = []
    for quant_set in product( *[l[1] for l in quantify_info] ):
        # Replace tokens for different quantifiers
        new_tokens = deepcopy(tokens)
        for i, num in enumerate(quant_set):
            tk_idx = quantify_info[i][0]
            new_tokens[tk_idx] = Token(TokenType.TOKEN_QUANTIFIER, num)

        # Remove quantifier of one
        new_tokens = [ tk for tk in new_tokens if not (tk.type.name == 'TOKEN_QUANTIFIER' and tk.value == 1) ] 

        record = str(new_tokens)
        if record not in records:
            results.append(new_tokens)
            records.add(record)

    print(records)
    return results
