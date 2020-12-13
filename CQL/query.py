from typing import Union
from lexer import Lexer
from parser_ import Parser
from interpreter import Interpreter
from expand_quantifiers import expand_quantifiers


def query(cql, default_attr:Union(str, int)="word", max_quant_num:int=15):
    """[summary]

    Parameters
    ----------
    cql : [type]
        [description]
    default_attr : Union, optional
        [description], by default "word"
    max_quant_num : int, optional
        [description], by default 15

    Returns
    -------
    [type]
        [description]
    """
    tokens = list(Lexer(cql).generate_tokens())
    parser = Parser(tokens)
    queries = expand_quantifiers(tokens, max_quant_num)

    values = []
    for query in queries:
        parser = Parser(query)
        tree = parser.parse()
        interpreter = Interpreter(default_attrname=default_attr)
        value = interpreter.visit(tree)
        if len(value) > 0:
            values.append(value)

    return values