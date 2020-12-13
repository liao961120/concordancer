from lexer import Lexer
from expand_quantifiers import expand_quantifiers
from parser_ import Parser
from interpreter import Interpreter, flatten_list

MAX_QUANT = 15
DEFAULT_ATTR_NAME = 'w'


while True:
    # try:
    text = input('CQL > ')
    lexer = Lexer(text)
    tokens = list(lexer.generate_tokens())
    print(f"tokens  : {tokens}")
    print()
    queries = expand_quantifiers(tokens, MAX_QUANT)

    values = []
    for query in queries:
        parser = Parser(query)
        tree = parser.parse()
        print(f"parser  : {tree}")
        print()
        interpreter = Interpreter(default_attrname=DEFAULT_ATTR_NAME)
        value = interpreter.visit(tree)
        if len(value) > 0:
            values.append(value)
        
    print(f"value   : {values}")
    # except Exception as e:
    #    print(e)
