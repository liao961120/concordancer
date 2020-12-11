import unittest
from tokens import Token, TokenType
from nodes import *
from lexer import Lexer
from parser_ import Parser

with open("backslash.txt") as f: 
    ESCAPE = f.read().strip()

class TestParser(unittest.TestCase):

    def test_empty(self):
        tokens = list(Lexer("").generate_tokens())
        parser = Parser(tokens)
        tree = parser.parse()
        self.assertEqual(tree, None)
    
    def test_words(self):
        tokens = list(Lexer('[x="z"] [x="z"]{1,2} lab:[]*').generate_tokens())
        parser = Parser(tokens)
        tree = parser.parse()
        self.assertEqual(tree, [
            AssignAttrNode(
                AttrNameNode("x"), 
                "is", 
                AttrValueNode("z")
            ),
            QuantifyNode(
                AssignAttrNode(
                    AttrNameNode("x"), 
                    "is", 
                    AttrValueNode("z")
                ),
                (1, 2)
            ),
            LabelNode(
                QuantifyNode(
                    EmptyTokenNode(),
                    (0, 'inf')
                ),
                'lab'
            )
        ])

    def test_wordGroups(self):
        tokens = list(Lexer('lab:([x="z" & word!="b"] [x="z"])?').generate_tokens())
        parser = Parser(tokens)
        tree = parser.parse()
        self.assertEqual(tree, [
            LabelNode(
                QuantifyNode(
                    [
                        ConjoinAttrNode(
                            AssignAttrNode(
                                AttrNameNode("x"),
                                "is",
                                AttrValueNode("z")
                            ),
                            AssignAttrNode(
                                AttrNameNode("word"),
                                "is_not",
                                AttrValueNode("b")
                            )
                        ),
                        AssignAttrNode(
                            AttrNameNode("x"),
                            "is",
                            AttrValueNode("z")
                        )
                    ],
                    (0, 1)
                ),
                'lab'
            )
        ])


if __name__ == "__main__":
    import os
    os.system("python3 -m unittest test_parser")

