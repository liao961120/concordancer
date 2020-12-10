from lexer import Lexer
from parser_ import Parser

while True:
    #try:
        text = input('CQL > ')
        lexer = Lexer(text)
        tokens = list(lexer.generate_tokens())
        print(tokens)
        print()
        parser = Parser(tokens)
        tree = parser.parse()
        print(tree)
    #except Exception as e:
    #    print(e)
