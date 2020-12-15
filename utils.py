import re
from typing import Union

REGEX_META = set('[].^$*+{}|()')
ESCAPE = chr(92)
SPECIAL_SET = {r'\d', r'\D', r'\s', r'\S', r'\w', r'\W'}


def match_corpus_token(values:list, tag:Union[str, int] , target: dict) -> bool:
    """Check whether all CQL generated values match a token in corpus

    Parameters
    ----------
    values : list
        A list of attribute values to check
    tag : Union[str, int]
        Attribute of the token
    target : dict
        A token object retrieved from the corpus

    Returns
    -------
    bool
        Match or not
    """
    matched_num = 0

    for value in values:
        value, mode = match_mode(value)
        if mode == "regex":
            if re.search(value, target[tag]):
                matched_num += 1
        if mode == "literal":
            if value == target[tag]:
                matched_num += 1
    
    return matched_num == len(values)



def match_mode(x: str):
    if is_regex(x):
        return x, "regex"
    return x.replace(ESCAPE, ''), "literal"


def is_regex(x: str) -> bool:
    prev = ''
    for this in x:
        if prev + this in SPECIAL_SET:
            return True
        if this in REGEX_META:
            if prev != ESCAPE:
                return True
        
        prev = this
    return False

