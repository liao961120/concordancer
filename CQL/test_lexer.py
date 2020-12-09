import unittest
from tokens import Token, TokenType
from lexer import Lexer

with open("backslash.txt") as f: 
    ESCAPE = f.read().strip()

class TestLexer(unittest.TestCase):
    
    def test_empty(self):
        tokens = list(Lexer("").generate_tokens())
        self.assertEqual(tokens, [])
    
    def test_empty(self):
        tokens = list(Lexer("  \t \t\t \n\n").generate_tokens())
        self.assertEqual(tokens, [])
    
    def test_empty_token(self):
        tokens = list(Lexer('[]').generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.EMPTY_TOKEN)
        ])

    def test_default_token(self):
        tokens = list(Lexer('"我們"').generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.DEFAULT_TOKEN, "我們")
        ])


    def test_attr(self):
        tokens = list(Lexer('[word="aaa" & pos!="N.*"]').generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.ATTR_NAME, "word"),
            Token(TokenType.ATTR_RELATION, "is"),
            Token(TokenType.ATTR_VALUE, "aaa"),
            Token(TokenType.ATTR_AND),
            Token(TokenType.ATTR_NAME, "pos"),
            Token(TokenType.ATTR_RELATION, "is_not"),
            Token(TokenType.ATTR_VALUE, "N.*"),
        ])
    
    def test_escape(self):
        tokens = list(Lexer('[word="\t"] [word!="\""]').generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.ATTR_NAME, "word"),
            Token(TokenType.ATTR_RELATION, "is"),
            Token(TokenType.ATTR_VALUE, "\t"),
            Token(TokenType.SEP),
            Token(TokenType.ATTR_NAME, "word"),
            Token(TokenType.ATTR_RELATION, "is_not"),
            Token(TokenType.ATTR_VALUE, '"'),
        ])

    def test_escape(self):
        with open("escape_quotes.txt") as f: txt = f.read()
        tokens = list(Lexer(txt).generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.DEFAULT_TOKEN, '"')
        ])
    
    def test_token_label(self):
        tokens = list(Lexer('abc:[] abc:"我們"').generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.TOKEN_LABEL, 'abc'),
            Token(TokenType.EMPTY_TOKEN),
            Token(TokenType.SEP),
            Token(TokenType.TOKEN_LABEL, 'abc'),
            Token(TokenType.DEFAULT_TOKEN, '我們'),
        ])
    
    def test_token_quatifier(self):
        tokens = list(Lexer('[]{1,2} []{2} []? []* []+').generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.EMPTY_TOKEN),
            Token(TokenType.TOKEN_QUANTIFIER, (1, 2)),
            Token(TokenType.SEP),
            Token(TokenType.EMPTY_TOKEN),
            Token(TokenType.TOKEN_QUANTIFIER, (2, 2)),
            Token(TokenType.SEP),
            Token(TokenType.EMPTY_TOKEN),
            Token(TokenType.TOKEN_QUANTIFIER, (0, 1)),
            Token(TokenType.SEP),
            Token(TokenType.EMPTY_TOKEN),
            Token(TokenType.TOKEN_QUANTIFIER, (0, 'inf')),
            Token(TokenType.SEP),
            Token(TokenType.EMPTY_TOKEN),
            Token(TokenType.TOKEN_QUANTIFIER, (1, 'inf')),
        ])
    
    def test_token_quatifier(self):
        tokens = list(Lexer('"我們"{1,2} "我們"{2} "我們"? "我們"* "我們"+').generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.DEFAULT_TOKEN, "我們"),
            Token(TokenType.TOKEN_QUANTIFIER, (1, 2)),
            Token(TokenType.SEP),
            Token(TokenType.DEFAULT_TOKEN, "我們"),
            Token(TokenType.TOKEN_QUANTIFIER, (2, 2)),
            Token(TokenType.SEP),
            Token(TokenType.DEFAULT_TOKEN, "我們"),
            Token(TokenType.TOKEN_QUANTIFIER, (0, 1)),
            Token(TokenType.SEP),
            Token(TokenType.DEFAULT_TOKEN, "我們"),
            Token(TokenType.TOKEN_QUANTIFIER, (0, 'inf')),
            Token(TokenType.SEP),
            Token(TokenType.DEFAULT_TOKEN, "我們"),
            Token(TokenType.TOKEN_QUANTIFIER, (1, 'inf')),
        ])
    

    def test_all(self):
        tokens = list(Lexer('[word="把" & pos="P"] [pos!="N[abcd].*|COMMACATEGORY|PERIODCATEGORY"]* obj:[pos="N[abcd].*"] v:[pos="V.*"]').generate_tokens())
        self.assertEqual(tokens, [
            Token(TokenType.ATTR_NAME, "word"),
            Token(TokenType.ATTR_RELATION, 'is'),
            Token(TokenType.ATTR_VALUE, '把'),
            Token(TokenType.ATTR_AND),
            Token(TokenType.ATTR_NAME, "pos"),
            Token(TokenType.ATTR_RELATION, 'is'),
            Token(TokenType.ATTR_VALUE, 'P'),
            Token(TokenType.SEP),
            Token(TokenType.ATTR_NAME, "pos"),
            Token(TokenType.ATTR_RELATION, 'is_not'),
            Token(TokenType.ATTR_VALUE, 'N[abcd].*|COMMACATEGORY|PERIODCATEGORY'),
            Token(TokenType.TOKEN_QUANTIFIER, (0, 'inf')),
            Token(TokenType.SEP),
            Token(TokenType.TOKEN_LABEL, 'obj'),
            Token(TokenType.ATTR_NAME, "pos"),
            Token(TokenType.ATTR_RELATION, 'is'),
            Token(TokenType.ATTR_VALUE, 'N[abcd].*'),
            Token(TokenType.SEP),
            Token(TokenType.TOKEN_LABEL, 'v'),
            Token(TokenType.ATTR_NAME, "pos"),
            Token(TokenType.ATTR_RELATION, 'is'),
            Token(TokenType.ATTR_VALUE, 'V.*')
        ])


if __name__ == "__main__":
    import os
    os.system("python3 -m unittest test_lexer")

