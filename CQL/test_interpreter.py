#%%
import unittest
from lexer import Lexer
from parser_ import Parser
from interpreter import Interpreter
from expand_quantifiers import expand_quantifiers
from deepdiff import DeepDiff


MAX_QUANT = 15
DFT_ATTR = 'w'


class TestInterpreter(unittest.TestCase):

    def test_word(self):
        values = generate_queries('"a" [word="b"] [word="c" & pos!="d"]')
        ans = [
            [
                {
                    'match': {DFT_ATTR: ["a"]},
                    'not_match': {}
                }, 
                {
                    'match': {'word': ["b"]},
                    'not_match': {}
                }, 
                {
                    'match': {'word': ["c"]},
                    'not_match': {'pos': ["d"]}
                }, 
            ]
        ]
        diff = DeepDiff(values, ans, ignore_order=True)
        self.assertEqual(diff, {})


    def test_group(self):
        values = generate_queries('"a" ([word="b"] [word="c" & pos!="d"])')
        ans = [
            [
                {
                    'match': {DFT_ATTR: ["a"]},
                    'not_match': {}
                }, 
                {
                    'match': {'word': ["b"]},
                    'not_match': {}
                }, 
                {
                    'match': {'word': ["c"]},
                    'not_match': {'pos': ["d"]}
                }, 
            ]
        ]
        diff = DeepDiff(values, ans, ignore_order=True)
        self.assertEqual(diff, {})


    def test_label(self):
        values = generate_queries('"a" lab:([word="b"] lab2:[word="c" & pos!="d"])')
        ans = [
            [
                {
                    'match': {DFT_ATTR: ["a"]},
                    'not_match': {}
                }, 
                {
                    'match': {'word': ["b"]},
                    'not_match': {},
                    '__label__': ['lab']
                }, 
                {
                    'match': {'word': ["c"]},
                    'not_match': {'pos': ["d"]},
                    '__label__': ['lab', 'lab2']
                }, 
            ]
        ]
        diff = DeepDiff(values, ans, ignore_order=True)
        self.assertEqual(diff, {})



def generate_queries(cql: str):
    
    tokens = list(Lexer(cql).generate_tokens())
    parser = Parser(tokens)
    queries = expand_quantifiers(tokens, MAX_QUANT)

    values = []
    for query in queries:
        parser = Parser(query)
        tree = parser.parse()
        interpreter = Interpreter(default_attrname=DFT_ATTR)
        value = interpreter.visit(tree)
        if len(value) > 0:
            values.append(value)

    return values


#%%
cql = '''
"a" [word="b"] [word="c" & pos!="d"]
'''
generate_queries(cql)


#%%
if __name__ == "__main__":
    import os
    os.system("python3 -m unittest test_interpreter")
