#%%
from lexer import Lexer
from tokens import Token, TokenType
from itertools import product
from copy import deepcopy

MAX_QUANT = 10

cql = '''
lab:("a" "b"{0,1}) "c"{2,3}
'''

lexer = Lexer(cql)
tokens = list(lexer.generate_tokens())

quantify_info = []
for i, tk in enumerate(tokens):
    if tk.type.name == 'TOKEN_QUANTIFIER':
        min_ = tk.value[0]
        max_ = tk.value[1] + 1 if tk.value[1] != 'inf' else MAX_QUANT
        
        quantify_info.append([i, 
            list(range(min_, max_))]
        )



results = []
for quant_set in product( *[l[1] for l in quantify_info] ):

    # replace tokens for different quantifiers
    new_tokens = deepcopy(tokens)
    for i, num in enumerate(quant_set):
        tk_idx = quantify_info[i][0]
        new_tokens[tk_idx] = Token(TokenType.TOKEN_QUANTIFIER, num)
    
    results.append(new_tokens)

# %%
