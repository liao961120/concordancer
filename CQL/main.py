from lexer import Lexer
from parser_ import Parser
from interpreter import Interpreter


while True:
    # try:
    text = input('CQL > ')
    lexer = Lexer(text)
    tokens = list(lexer.generate_tokens())
    print(f"tokens  : {tokens}")
    print()
    parser = Parser(tokens)
    tree = parser.parse()
    print(f"parser  : {tree}")
    interpreter = Interpreter(default_attrname='w', quantifier_max=5)
    value = interpreter.visit(tree)
    print(f"value   : {value}")
    # except Exception as e:
    #    print(e)
