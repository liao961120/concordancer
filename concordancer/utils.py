import re
from typing import Union

REGEX_META = set('[].^$*+{}|()')
ESCAPE = chr(92)
SPECIAL_SET = {r'\d', r'\D', r'\s', r'\S', r'\w', r'\W'}

def queryMatchToken(queryTerm: dict, corpToken: dict):
    if 'match' in queryTerm:
        positive_matched_tag = 0
        for tag, values in queryTerm.get('match').items():
            if tag not in corpToken: return False
            if allValues_match_token(values, tag, corpToken): 
                positive_matched_tag += 1
        
        if positive_matched_tag != len(queryTerm.get('match')):
            return False
    
    if 'not_match' in queryTerm:
        negative_matched_tag = 0
        counter = 0
        for tag, values in queryTerm.get('not_match').items():
            taget_value = queryTerm.get('not_match').get(tag)
            for value in values:
                counter += 1
                value, mode = match_mode(value)
                if mode == "literal":
                    if value != taget_value:
                        negative_matched_tag += 1
                else:
                    if (taget_value != None) and re.search(value, taget_value):
                        negative_matched_tag += 1
        
        if negative_matched_tag != counter:
            return False
    
    return True



def allValues_match_token(values:list, tag:Union[str, int] , target: dict) -> bool:
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

