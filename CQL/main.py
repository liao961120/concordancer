from lexer import Lexer

while True:
    try:
        text = input('CQL > ')
        lexer = Lexer(text)
        tokens = list(lexer.generate_tokens())
        print(tokens)
    except Exception as e:
        print(e)
